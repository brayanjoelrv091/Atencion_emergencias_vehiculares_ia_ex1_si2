"""
P2 — Motor de Clasificación Automática de Incidentes (CU8).

Arquitectura de clasificación multi-motor:
    1. YOLOv8  → Análisis de imágenes (detección de daños vehiculares)
    2. Whisper  → Transcripción de audio → análisis de texto
    3. Reglas   → Fallback basado en keywords ponderados

El resultado final combina los motores disponibles.
"""

import logging
import re
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════
# TIPOS Y CONSTANTES
# ═══════════════════════════════════════════════════════════════════════

CATEGORIAS = (
    "mecanico",
    "electrico",
    "carroceria",
    "neumaticos",
    "emergencia_vial",
    "otro",
)

SEVERIDADES = ("leve", "moderado", "grave", "critico")

# Keywords ponderados por categoría (peso mayor = más relevante)
KEYWORD_MAP: dict[str, list[tuple[str, float]]] = {
    "mecanico": [
        ("motor", 3.0), ("aceite", 2.5), ("freno", 2.5), ("transmision", 2.0),
        ("embrague", 2.0), ("radiador", 2.0), ("caja", 1.5), ("correa", 1.5),
        ("refrigerante", 1.5), ("calentamiento", 2.0), ("arranque", 1.5),
        ("fuga", 2.0), ("humo", 2.5), ("ruido", 1.5), ("vibracion", 1.5),
        ("recalentamiento", 3.0), ("bomba", 1.5), ("escape", 1.5),
    ],
    "electrico": [
        ("bateria", 3.0), ("alternador", 2.5), ("fusible", 2.0), ("luces", 2.0),
        ("electrico", 2.5), ("cables", 1.5), ("cortocircuito", 3.0),
        ("electronica", 2.0), ("sensor", 2.0), ("tablero", 1.5),
        ("computadora", 2.0), ("chispa", 2.0), ("encendido", 1.5),
    ],
    "carroceria": [
        ("choque", 3.0), ("golpe", 2.5), ("abolladur", 2.5), ("rayado", 2.0),
        ("parabrisas", 2.5), ("pintura", 1.5), ("paragolpe", 2.0),
        ("puerta", 1.5), ("espejo", 1.5), ("vidrio", 2.0), ("roto", 2.0),
        ("impacto", 2.5), ("accidente", 3.0), ("colision", 3.0),
        ("capo", 1.5), ("techo", 1.5), ("volca", 3.0),
    ],
    "neumaticos": [
        ("llanta", 3.0), ("neumatico", 3.0), ("pinchaz", 3.0), ("poncha", 3.0),
        ("rueda", 2.5), ("desinflad", 2.5), ("caucho", 2.0), ("revent", 3.0),
        ("rim", 1.5), ("aro", 1.5), ("alineacion", 1.5), ("balanceo", 1.5),
    ],
    "emergencia_vial": [
        ("incendio", 3.0), ("fuego", 3.0), ("volcamiento", 3.0),
        ("atropello", 3.0), ("emergencia", 2.5), ("herido", 3.0),
        ("varado", 2.0), ("inundacion", 2.5), ("derrumbe", 2.5),
        ("peligro", 2.0), ("auxilio", 2.5), ("sos", 3.0), ("grave", 2.0),
        ("atrapado", 3.0), ("ambulancia", 3.0),
    ],
}

# Keywords de severidad
SEVERITY_KEYWORDS: dict[str, list[tuple[str, float]]] = {
    "critico": [
        ("incendio", 3.0), ("fuego", 3.0), ("volcamiento", 3.0), ("herido", 3.0),
        ("muert", 3.0), ("atrapado", 3.0), ("explosion", 3.0), ("ambulancia", 2.5),
        ("grave", 2.5), ("sos", 3.0), ("urgente", 2.5),
    ],
    "grave": [
        ("accidente", 2.5), ("choque", 2.5), ("colision", 2.5), ("humo", 2.0),
        ("fuga", 2.0), ("cortocircuito", 2.0), ("recalentamiento", 2.0),
        ("revent", 2.0), ("varado", 1.5), ("inmovil", 2.0),
    ],
    "moderado": [
        ("ruido", 1.5), ("vibracion", 1.5), ("falla", 1.5), ("problema", 1.5),
        ("averia", 1.5), ("dano", 1.5), ("golpe", 1.5), ("pinchaz", 1.5),
    ],
    "leve": [
        ("rayado", 1.0), ("revision", 1.0), ("mantenimiento", 1.0),
        ("consulta", 1.0), ("inspeccionar", 1.0), ("menor", 1.0),
    ],
}

# Mapeo YOLOv8 → categoría del sistema
YOLO_CLASS_MAP: dict[str, str] = {
    "car": "carroceria",
    "truck": "carroceria",
    "bus": "carroceria",
    "motorcycle": "carroceria",
    "fire": "emergencia_vial",
    "smoke": "emergencia_vial",
}


@dataclass
class ClassificationResult:
    """Resultado de la clasificación de un incidente."""
    categoria: str = "otro"
    severidad: str = "moderado"
    confianza: float = 0.5
    razonamiento: str = ""
    metodo: str = "reglas"


@dataclass
class _EngineResult:
    """Resultado parcial de un motor individual."""
    categoria: str = "otro"
    severidad: str = "moderado"
    confianza: float = 0.0
    razonamiento: str = ""
    exitoso: bool = False


# ═══════════════════════════════════════════════════════════════════════
# CLASIFICADOR PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════

class IncidentClassifier:
    """
    Clasificador multimodal de incidentes vehiculares.

    Prioridad de motores:
        1. YOLOv8 (imágenes) — si hay fotos y el modelo está disponible
        2. Whisper (audio) — transcribe y luego clasifica texto
        3. Reglas (texto) — siempre disponible como fallback

    El resultado final combina las señales de cada motor disponible.
    """

    def __init__(self):
        self._yolo_model = None
        self._whisper_model = None
        self._yolo_available = False
        self._whisper_available = False
        self._init_models()

    def _init_models(self):
        """Carga lazy de modelos pesados de IA."""
        # ── YOLOv8 ──
        try:
            from ultralytics import YOLO
            from app.core.config import settings

            self._yolo_model = YOLO(settings.YOLO_MODEL_PATH)
            self._yolo_available = True
            logger.info("✅ YOLOv8 cargado correctamente")
        except ImportError:
            logger.warning("⚠️ ultralytics no instalado — YOLOv8 deshabilitado")
        except Exception as e:
            logger.warning(f"⚠️ Error cargando YOLOv8: {e}")

        # ── Whisper ──
        try:
            import whisper
            from app.core.config import settings

            self._whisper_model = whisper.load_model(settings.WHISPER_MODEL_SIZE)
            self._whisper_available = True
            logger.info("✅ Whisper cargado correctamente")
        except ImportError:
            logger.warning("⚠️ openai-whisper no instalado — Whisper deshabilitado")
        except Exception as e:
            logger.warning(f"⚠️ Error cargando Whisper: {e}")

    # ── Motor 1: Clasificación por reglas (texto) ───────────────────

    def classify_text(self, text: str) -> _EngineResult:
        """Clasifica un incidente usando análisis de keywords ponderados."""
        if not text or not text.strip():
            return _EngineResult(razonamiento="Sin texto para analizar")

        normalized = text.lower().strip()
        # Quitar acentos para matching más robusto
        replacements = {
            "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ñ": "n"
        }
        for acc, plain in replacements.items():
            normalized = normalized.replace(acc, plain)

        # Calcular scores por categoría
        cat_scores: dict[str, float] = {}
        cat_matches: dict[str, list[str]] = {}
        for cat, keywords in KEYWORD_MAP.items():
            score = 0.0
            matches = []
            for kw, weight in keywords:
                if kw in normalized:
                    score += weight
                    matches.append(kw)
            if score > 0:
                cat_scores[cat] = score
                cat_matches[cat] = matches

        # Mejor categoría
        if cat_scores:
            best_cat = max(cat_scores, key=cat_scores.get)  # type: ignore[arg-type]
            max_score = cat_scores[best_cat]
            total = sum(cat_scores.values())
            confianza = min(0.95, max_score / max(total, 1.0))
        else:
            best_cat = "otro"
            confianza = 0.3
            cat_matches = {}

        # Calcular severidad
        sev_scores: dict[str, float] = {}
        for sev, keywords in SEVERITY_KEYWORDS.items():
            score = sum(w for kw, w in keywords if kw in normalized)
            if score > 0:
                sev_scores[sev] = score

        if sev_scores:
            best_sev = max(sev_scores, key=sev_scores.get)  # type: ignore[arg-type]
        else:
            best_sev = "moderado"

        # Razonamiento
        matched = cat_matches.get(best_cat, [])
        reasoning = (
            f"[Reglas] Categoría '{best_cat}' determinada por keywords: "
            f"{', '.join(matched) if matched else 'ninguno'}. "
            f"Severidad '{best_sev}'."
        )

        return _EngineResult(
            categoria=best_cat,
            severidad=best_sev,
            confianza=confianza,
            razonamiento=reasoning,
            exitoso=True,
        )

    # ── Motor 2: YOLOv8 (imágenes) ─────────────────────────────────

    def classify_image(self, image_path: str) -> _EngineResult:
        """Clasifica un incidente analizando una imagen con YOLOv8."""
        if not self._yolo_available or self._yolo_model is None:
            return _EngineResult(razonamiento="YOLOv8 no disponible")

        try:
            results = self._yolo_model(image_path, verbose=False)
            if not results or not results[0].boxes:
                return _EngineResult(
                    razonamiento="YOLOv8 no detectó objetos relevantes"
                )

            # Analizar detecciones
            detections = []
            for box in results[0].boxes:
                cls_id = int(box.cls[0])
                cls_name = results[0].names[cls_id]
                conf = float(box.conf[0])
                detections.append((cls_name, conf))

            # Mapear detecciones a categorías del sistema
            cat_votes: dict[str, float] = {}
            for cls_name, conf in detections:
                mapped = YOLO_CLASS_MAP.get(cls_name, "otro")
                cat_votes[mapped] = cat_votes.get(mapped, 0) + conf

            if cat_votes:
                best = max(cat_votes, key=cat_votes.get)  # type: ignore[arg-type]
                avg_conf = cat_votes[best] / max(
                    1, sum(1 for c, _ in detections if YOLO_CLASS_MAP.get(c) == best)
                )
            else:
                best = "otro"
                avg_conf = 0.3

            det_str = ", ".join(f"{n}({c:.2f})" for n, c in detections[:5])
            reasoning = f"[YOLOv8] Detecciones: {det_str}. Categoría: '{best}'."

            return _EngineResult(
                categoria=best,
                severidad="moderado",  # YOLOv8 standard no detecta severidad
                confianza=min(0.9, avg_conf),
                razonamiento=reasoning,
                exitoso=True,
            )
        except Exception as e:
            logger.error(f"Error en YOLOv8: {e}")
            return _EngineResult(razonamiento=f"Error YOLOv8: {e}")

    # ── Motor 3: Whisper (audio → texto) ────────────────────────────

    def transcribe_audio(self, audio_path: str) -> str:
        """Transcribe un archivo de audio a texto usando Whisper."""
        if not self._whisper_available or self._whisper_model is None:
            logger.warning("Whisper no disponible para transcripción")
            return ""

        try:
            result = self._whisper_model.transcribe(audio_path, language="es")
            text = result.get("text", "").strip()
            logger.info(f"Whisper transcripción: {text[:100]}...")
            return text
        except Exception as e:
            logger.error(f"Error en Whisper: {e}")
            return ""

    def classify_audio(self, audio_path: str) -> _EngineResult:
        """Transcribe audio con Whisper y clasifica el texto resultante."""
        transcription = self.transcribe_audio(audio_path)
        if not transcription:
            return _EngineResult(razonamiento="No se pudo transcribir el audio")

        result = self.classify_text(transcription)
        result.razonamiento = (
            f"[Whisper] Transcripción: \"{transcription[:200]}\" → "
            f"{result.razonamiento}"
        )
        result.metodo = "whisper"
        return result

    # ── Clasificación combinada ─────────────────────────────────────

    def classify(
        self,
        text: str = "",
        image_paths: list[str] | None = None,
        audio_path: str | None = None,
    ) -> ClassificationResult:
        """
        Clasificación multimodal combinada.

        Prioridad: YOLOv8 > Whisper > Reglas.
        Si múltiples motores coinciden, aumenta la confianza.
        """
        engines: list[_EngineResult] = []

        # 1. Imágenes (YOLOv8)
        if image_paths:
            for img in image_paths[:3]:  # Máximo 3 imágenes
                res = self.classify_image(img)
                if res.exitoso:
                    engines.append(res)

        # 2. Audio (Whisper)
        if audio_path:
            res = self.classify_audio(audio_path)
            if res.exitoso:
                engines.append(res)

        # 3. Texto (Reglas) — siempre se ejecuta como fallback
        if text:
            res = self.classify_text(text)
            if res.exitoso:
                engines.append(res)

        # Si ningún motor produjo resultado
        if not engines:
            return ClassificationResult(
                categoria="otro",
                severidad="moderado",
                confianza=0.3,
                razonamiento="No se pudo clasificar: sin datos suficientes.",
                metodo="ninguno",
            )

        # Combinar resultados: votar por categoría
        cat_votes: dict[str, float] = {}
        sev_votes: dict[str, float] = {}
        reasonings: list[str] = []

        for eng in engines:
            cat_votes[eng.categoria] = (
                cat_votes.get(eng.categoria, 0) + eng.confianza
            )
            sev_votes[eng.severidad] = (
                sev_votes.get(eng.severidad, 0) + eng.confianza
            )
            if eng.razonamiento:
                reasonings.append(eng.razonamiento)

        best_cat = max(cat_votes, key=cat_votes.get)  # type: ignore[arg-type]
        best_sev = max(sev_votes, key=sev_votes.get)  # type: ignore[arg-type]

        # Confianza: promedio ponderado + bonus por consenso
        avg_conf = sum(e.confianza for e in engines) / len(engines)
        consensus_bonus = 0.1 if len(engines) > 1 and all(
            e.categoria == best_cat for e in engines
        ) else 0.0
        final_conf = min(0.99, avg_conf + consensus_bonus)

        # Determinar método
        methods = set()
        if any(self._yolo_available and "YOLOv8" in e.razonamiento for e in engines):
            methods.add("yolo")
        if any("Whisper" in e.razonamiento for e in engines):
            methods.add("whisper")
        if any("Reglas" in e.razonamiento for e in engines):
            methods.add("reglas")
        method = "combinado" if len(methods) > 1 else (methods.pop() if methods else "reglas")

        return ClassificationResult(
            categoria=best_cat,
            severidad=best_sev,
            confianza=round(final_conf, 4),
            razonamiento=" | ".join(reasonings),
            metodo=method,
        )


# Singleton del clasificador
_classifier: IncidentClassifier | None = None


def get_classifier() -> IncidentClassifier:
    """Retorna instancia singleton del clasificador."""
    global _classifier
    if _classifier is None:
        _classifier = IncidentClassifier()
    return _classifier
