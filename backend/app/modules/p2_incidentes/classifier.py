"""
P2 — Clasificador Multimodal de Incidentes Vehiculares (IA en la Nube).

Arquitectura:
    ┌─────────────┐     ┌──────────────────┐
    │  Audio .m4a  │────▶│ Groq Whisper API  │──▶ Texto transcrito
    └─────────────┘     └──────────────────┘
    ┌─────────────┐     ┌──────────────────┐
    │  Texto desc  │────▶│ Groq Llama 3 API │──▶ Clasificación JSON
    └─────────────┘     └──────────────────┘
    ┌─────────────┐     ┌──────────────────┐
    │  Foto .jpg   │────▶│ Roboflow Detect  │──▶ Detecciones + confianza
    └─────────────┘     └──────────────────┘

Motores:
    1. Groq Whisper  → transcripción de audio a texto (whisper-large-v3-turbo)
    2. Groq LLM      → análisis inteligente del texto (llama-3.1-8b-instant)
    3. Roboflow       → detección de daños en imágenes (rutai-vision-pro/2)

Autor: RutAIGeoProxi — Monolito Modular
"""

import json
import logging
from dataclasses import dataclass
from pathlib import Path

import httpx

from app.shared.config import settings

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

# ── Mapeo de clases de Roboflow → categorías del sistema ─────────────
# Las claves dependen de las etiquetas que usaste al anotar en Roboflow.
# Se usa .lower() antes de buscar para evitar problemas de capitalización.
ROBOFLOW_CLASS_MAP: dict[str, str] = {
    # ═══════════════════════════════════════════════════════════════════
    # TUS 4 CLASES EXACTAS de rutai-vision-pro/2 (las que entrenaste)
    # ═══════════════════════════════════════════════════════════════════
    "choque":              "carroceria",
    "llanta_pinchada":     "neumaticos",
    "problema_motor":      "mecanico",
    "problema_bateria":    "electrico",
    # ═══════════════════════════════════════════════════════════════════
    # Variantes comunes (por si Roboflow normaliza los nombres)
    # ═══════════════════════════════════════════════════════════════════
    # ── Carrocería / Colisión ──
    "colision":          "carroceria",
    "accidente":         "carroceria",
    "dano":              "carroceria",
    "abolladura":        "carroceria",
    "rayado":            "carroceria",
    "scratch":           "carroceria",
    "dent":              "carroceria",
    "broken_glass":      "carroceria",
    "vidrio_roto":       "carroceria",
    "golpe":             "carroceria",
    "impacto":           "carroceria",
    "damage":            "carroceria",
    "car":               "carroceria",
    "vehicle":           "carroceria",
    "vehicle_damage":    "carroceria",
    "car_damage":        "carroceria",
    # ── Neumáticos ──
    "llanta":            "neumaticos",
    "flat_tire":         "neumaticos",
    "neumatico":         "neumaticos",
    "pinchazo":          "neumaticos",
    "ponchadura":        "neumaticos",
    "tire":              "neumaticos",
    # ── Mecánico ──
    "motor":             "mecanico",
    "engine":            "mecanico",
    "engine_compartment": "mecanico",
    "humo_motor":        "mecanico",
    "fuga":              "mecanico",
    # ── Eléctrico ──
    "electrico":         "electrico",
    "bateria":           "electrico",
    "cables":            "electrico",
    # ── Emergencia vial ──
    "incendio":          "emergencia_vial",
    "fuego":             "emergencia_vial",
    "fire":              "emergencia_vial",
    "smoke":             "emergencia_vial",
    "volcamiento":       "emergencia_vial",
    "volcadura":         "emergencia_vial",
}


# ═══════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class ClassificationResult:
    """Resultado final de la clasificación multimodal."""
    categoria: str = "otro"
    severidad: str = "moderado"
    confianza: float = 0.5
    razonamiento: str = ""
    metodo: str = "reglas"


@dataclass
class _EngineResult:
    """Resultado parcial de un motor de IA individual."""
    categoria: str = "otro"
    severidad: str = "moderado"
    confianza: float = 0.0
    razonamiento: str = ""
    exitoso: bool = False


# ═══════════════════════════════════════════════════════════════════════
# CLASIFICADOR PRINCIPAL (APIs en la Nube)
# ═══════════════════════════════════════════════════════════════════════

class IncidentClassifier:
    """
    Clasificador multimodal de incidentes vehiculares.

    Consume APIs externas (Groq + Roboflow) en lugar de modelos locales.
    Esto permite que el backend sea ultra-ligero (~50 MB) y funcione
    en servidores gratuitos (Render) sin problemas de RAM.

    Flujo:
        1. Si hay audio → Groq Whisper lo transcribe a texto
        2. Texto (original + transcripción) → Groq Llama 3 clasifica
        3. Si hay imagen → Roboflow detecta daños visualmente
        4. Se combinan los resultados con voto ponderado por confianza
    """

    # Timeout generoso para evitar falsos errores en redes lentas
    _HTTP_TIMEOUT = 30.0

    def __init__(self) -> None:
        self._groq_key = settings.GROQ_API_KEY
        self._rf_key = settings.ROBOFLOW_API_KEY
        self._rf_model = settings.ROBOFLOW_MODEL
        self._rf_version = settings.ROBOFLOW_VERSION

        if not self._groq_key:
            logger.warning(
                "⚠️  GROQ_API_KEY no configurada — "
                "Transcripción de audio y análisis LLM deshabilitados."
            )
        if not self._rf_key:
            logger.warning(
                "⚠️  ROBOFLOW_API_KEY no configurada — "
                "Detección visual de daños deshabilitada."
            )
        else:
            logger.info(
                f"✅ Roboflow configurado → modelo: {self._rf_model}/{self._rf_version}"
            )

    # ──────────────────────────────────────────────────────────────────
    # Motor 1: Groq Whisper — Audio → Texto
    # ──────────────────────────────────────────────────────────────────

    async def transcribe_audio_groq(self, audio_path: str) -> str:
        """
        Transcribe un archivo de audio a texto usando Groq Whisper API.

        Modelo: whisper-large-v3-turbo (más rápido, misma calidad).
        Idioma forzado a español para mejor precisión en reportes vehiculares.
        """
        if not self._groq_key:
            logger.warning("Groq no configurado, saltando transcripción de audio")
            return ""

        audio_file_path = Path(audio_path)
        if not audio_file_path.exists():
            logger.error(f"Archivo de audio no encontrado: {audio_path}")
            return ""

        url = "https://api.groq.com/openai/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {self._groq_key}"}

        try:
            async with httpx.AsyncClient(timeout=self._HTTP_TIMEOUT) as client:
                with open(audio_path, "rb") as f:
                    files = {
                        "file": (audio_file_path.name, f, "audio/mpeg"),
                        "model": (None, "whisper-large-v3-turbo"),
                        "language": (None, "es"),
                        "response_format": (None, "json"),
                    }
                    resp = await client.post(url, headers=headers, files=files)
                    resp.raise_for_status()

                    text = resp.json().get("text", "").strip()
                    logger.info(f"🎤 Groq Whisper transcripción: «{text[:120]}»")
                    return text

        except httpx.HTTPStatusError as e:
            logger.error(
                f"Groq Whisper HTTP {e.response.status_code}: "
                f"{e.response.text[:300]}"
            )
        except Exception as e:
            logger.error(f"Groq Whisper error inesperado: {e}")

        return ""

    # ──────────────────────────────────────────────────────────────────
    # Motor 2: Groq LLM (Llama 3) — Texto → Clasificación JSON
    # ──────────────────────────────────────────────────────────────────

    async def classify_text_groq(self, text: str) -> _EngineResult:
        """
        Usa Llama 3.1 8B en Groq para clasificar el reporte de texto.

        El LLM recibe un prompt estructurado y devuelve JSON con:
        - categoria (una de las 6 del sistema)
        - severidad (leve/moderado/grave/critico)
        - razonamiento (explicación breve)

        Ventaja sobre reglas: entiende contexto, sinónimos y lenguaje coloquial.
        """
        if not self._groq_key or not text or not text.strip():
            return _EngineResult(razonamiento="Sin texto o Groq no configurado")

        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._groq_key}",
            "Content-Type": "application/json",
        }

        system_prompt = (
            "Eres un sistema experto en clasificación de incidentes vehiculares "
            "para una plataforma de asistencia en carreteras llamada RutAIGeoProxi. "
            "Tu trabajo es analizar reportes de incidentes y clasificarlos.\n\n"
            "CATEGORÍAS VÁLIDAS (usa exactamente estos valores):\n"
            "- mecanico: problemas de motor, frenos, transmisión, fugas, humo del motor\n"
            "- electrico: batería, alternador, fusibles, luces, cortocircuito, sensores\n"
            "- carroceria: choques, golpes, abolladuras, vidrios rotos, pintura dañada\n"
            "- neumaticos: llanta ponchada/pinchada, neumático reventado, desinflado\n"
            "- emergencia_vial: incendio, volcamiento, heridos, atrapados, peligro grave\n"
            "- otro: no encaja en ninguna categoría anterior\n\n"
            "SEVERIDADES VÁLIDAS:\n"
            "- leve: rayones menores, mantenimiento preventivo, consultas\n"
            "- moderado: fallas mecánicas controlables, daños parciales\n"
            "- grave: accidentes con daño significativo, vehículo inmovilizado\n"
            "- critico: incendio, volcamiento, heridos, riesgo de vida\n\n"
            "Responde ÚNICAMENTE con un JSON válido."
        )

        user_prompt = (
            f"Clasifica este reporte de incidente vehicular:\n\n"
            f"«{text}»\n\n"
            f"Responde con este formato JSON exacto:\n"
            f'{{"categoria": "...", "severidad": "...", "razonamiento": "..."}}'
        )

        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.1,
            "max_tokens": 256,
        }

        try:
            async with httpx.AsyncClient(timeout=self._HTTP_TIMEOUT) as client:
                resp = await client.post(url, headers=headers, json=payload)
                resp.raise_for_status()

                content = resp.json()["choices"][0]["message"]["content"]
                data = json.loads(content)

                categoria = data.get("categoria", "otro")
                severidad = data.get("severidad", "moderado")
                razon = data.get("razonamiento", "Sin razonamiento del LLM")

                # Validar que los valores sean los esperados
                if categoria not in CATEGORIAS:
                    logger.warning(f"LLM devolvió categoría inválida: {categoria}")
                    categoria = "otro"
                if severidad not in SEVERIDADES:
                    logger.warning(f"LLM devolvió severidad inválida: {severidad}")
                    severidad = "moderado"

                logger.info(
                    f"🧠 Groq LLM → cat={categoria}, sev={severidad}, "
                    f"razón=«{razon[:80]}»"
                )

                return _EngineResult(
                    categoria=categoria,
                    severidad=severidad,
                    confianza=0.90,
                    razonamiento=f"[Groq-LLM] {razon}",
                    exitoso=True,
                )

        except httpx.HTTPStatusError as e:
            logger.error(
                f"Groq LLM HTTP {e.response.status_code}: "
                f"{e.response.text[:300]}"
            )
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Groq LLM respuesta malformada: {e}")
        except Exception as e:
            logger.error(f"Groq LLM error inesperado: {e}")

        return _EngineResult(razonamiento="Error al analizar texto con Groq LLM")

    # ──────────────────────────────────────────────────────────────────
    # Motor 3: Roboflow — Imagen → Detección de Daños
    # ──────────────────────────────────────────────────────────────────

    async def classify_image_roboflow(self, image_path: str) -> _EngineResult:
        """
        Envía una imagen al modelo entrenado en Roboflow para detectar
        daños vehiculares visualmente.

        Endpoint: https://detect.roboflow.com/{model}/{version}
        El modelo `rutai-vision-pro/2` fue entrenado con imágenes de
        choques, abolladuras, llantas ponchadas, etc.
        """
        if not self._rf_key:
            return _EngineResult(razonamiento="Roboflow no configurado")

        img_path = Path(image_path)
        if not img_path.exists():
            logger.error(f"Imagen no encontrada: {image_path}")
            return _EngineResult(razonamiento=f"Imagen no encontrada: {image_path}")

        # Roboflow Inference API URL
        url = f"https://detect.roboflow.com/{self._rf_model}/{self._rf_version}"
        params = {
            "api_key": self._rf_key,
            "confidence": 25,   # Umbral mínimo de confianza (25%)
            "overlap": 30,      # Máximo solapamiento entre detecciones (30%)
        }

        try:
            async with httpx.AsyncClient(timeout=self._HTTP_TIMEOUT) as client:
                # Roboflow acepta la imagen como cuerpo binario
                image_bytes = img_path.read_bytes()
                resp = await client.post(
                    url,
                    params=params,
                    content=image_bytes,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                resp.raise_for_status()
                data = resp.json()

                predictions = data.get("predictions", [])
                if not predictions:
                    logger.info("📸 Roboflow: sin detecciones en la imagen")
                    return _EngineResult(
                        categoria="otro",
                        severidad="leve",
                        confianza=0.3,
                        razonamiento=(
                            "[Roboflow] No se detectaron daños visibles en la imagen. "
                            "El vehículo podría tener un problema no visible externamente."
                        ),
                        exitoso=True,
                    )

                # Tomar la detección con mayor confianza
                best = max(predictions, key=lambda p: p.get("confidence", 0))
                label = best.get("class", "desconocido")
                conf = best.get("confidence", 0.0)

                # Mapear la clase detectada a una categoría del sistema
                label_lower = label.lower().replace(" ", "_").replace("-", "_")
                categoria = ROBOFLOW_CLASS_MAP.get(label_lower, "carroceria")

                # Determinar severidad por confianza visual
                if conf >= 0.85:
                    severidad = "grave"
                elif conf >= 0.60:
                    severidad = "moderado"
                else:
                    severidad = "leve"

                # Listar todas las detecciones para el razonamiento
                det_list = [
                    f"{p['class']}({p['confidence']:.0%})"
                    for p in predictions[:5]
                ]
                det_str = ", ".join(det_list)

                logger.info(
                    f"📸 Roboflow → mejor: {label}({conf:.0%}), "
                    f"total: {len(predictions)} detecciones"
                )

                return _EngineResult(
                    categoria=categoria,
                    severidad=severidad,
                    confianza=round(conf, 4),
                    razonamiento=(
                        f"[Roboflow] Detecciones: {det_str}. "
                        f"Categoría asignada: '{categoria}' "
                        f"(clase principal: '{label}', confianza: {conf:.0%})"
                    ),
                    exitoso=True,
                )

        except httpx.HTTPStatusError as e:
            body = e.response.text[:300] if e.response else "sin cuerpo"
            logger.error(f"Roboflow HTTP {e.response.status_code}: {body}")
            return _EngineResult(
                razonamiento=f"Error HTTP {e.response.status_code} en Roboflow"
            )
        except Exception as e:
            logger.error(f"Roboflow error inesperado: {e}")
            return _EngineResult(razonamiento=f"Error inesperado en Roboflow: {e}")

    # ──────────────────────────────────────────────────────────────────
    # Clasificación Combinada (Orquestador)
    # ──────────────────────────────────────────────────────────────────

    async def classify(
        self,
        text: str = "",
        image_paths: list[str] | None = None,
        audio_path: str | None = None,
    ) -> ClassificationResult:
        """
        Clasificación multimodal combinada.

        Flujo:
            1. Audio (si existe) → Groq Whisper → se agrega al texto
            2. Texto → Groq LLM → clasificación inteligente
            3. Imagen (si existe) → Roboflow → detección visual
            4. Votación ponderada por confianza

        Si múltiples motores coinciden en categoría, se aplica un bonus
        de consenso (+10%) a la confianza final.
        """
        engines: list[_EngineResult] = []
        transcription = ""

        # ── Paso 1: Transcribir audio si existe ──
        if audio_path:
            transcription = await self.transcribe_audio_groq(audio_path)
            if transcription:
                # Concatenar transcripción al texto para enriquecer el análisis
                text = f"{text}. {transcription}".strip(". ")
                logger.info(f"Texto enriquecido con audio: «{text[:150]}»")

        # ── Paso 2: Clasificar texto con LLM ──
        if text and text.strip():
            res_text = await self.classify_text_groq(text)
            if res_text.exitoso:
                engines.append(res_text)

        # ── Paso 3: Clasificar imagen con Roboflow ──
        if image_paths:
            for img in image_paths[:2]:  # Máximo 2 imágenes para velocidad
                res_img = await self.classify_image_roboflow(img)
                if res_img.exitoso:
                    engines.append(res_img)

        # ── Sin resultados de ningún motor ──
        if not engines:
            logger.warning("⚠️ Ningún motor de IA produjo resultado")
            return ClassificationResult(
                categoria="otro",
                severidad="moderado",
                confianza=0.3,
                razonamiento=(
                    "No se pudo clasificar automáticamente. "
                    "Ningún motor de IA (Groq/Roboflow) produjo un resultado válido."
                ),
                metodo="fallback",
            )

        # ── Votación ponderada ──
        cat_scores: dict[str, float] = {}
        sev_scores: dict[str, float] = {}
        razones: list[str] = []

        for eng in engines:
            cat_scores[eng.categoria] = (
                cat_scores.get(eng.categoria, 0.0) + eng.confianza
            )
            sev_scores[eng.severidad] = (
                sev_scores.get(eng.severidad, 0.0) + eng.confianza
            )
            if eng.razonamiento:
                razones.append(eng.razonamiento)

        best_cat = max(cat_scores, key=lambda k: cat_scores[k])
        best_sev = max(sev_scores, key=lambda k: sev_scores[k])

        # Confianza promedio + bonus de consenso
        avg_conf = sum(e.confianza for e in engines) / len(engines)
        all_agree = len(engines) > 1 and all(
            e.categoria == best_cat for e in engines
        )
        consensus_bonus = 0.08 if all_agree else 0.0
        final_conf = min(0.99, round(avg_conf + consensus_bonus, 4))

        # Método usado
        metodos = set()
        for eng in engines:
            if "Groq-LLM" in eng.razonamiento:
                metodos.add("LLM")
            if "Roboflow" in eng.razonamiento:
                metodos.add("Vision")
        if transcription:
            metodos.add("Whisper")

        metodo = "IA-Cloud"
        if metodos:
            metodo = f"IA-Cloud ({'+'.join(sorted(metodos))})"

        # Razonamiento combinado
        razonamiento_final = " | ".join(razones)
        if transcription:
            razonamiento_final += (
                f" | 🎤 Transcripción: «{transcription[:120]}»"
            )

        logger.info(
            f"✅ Clasificación final → cat={best_cat}, sev={best_sev}, "
            f"conf={final_conf}, método={metodo}"
        )

        return ClassificationResult(
            categoria=best_cat,
            severidad=best_sev,
            confianza=final_conf,
            razonamiento=razonamiento_final,
            metodo=metodo,
        )


# ═══════════════════════════════════════════════════════════════════════
# SINGLETON
# ═══════════════════════════════════════════════════════════════════════

_classifier: IncidentClassifier | None = None


def get_classifier() -> IncidentClassifier:
    """Retorna instancia singleton del clasificador."""
    global _classifier
    if _classifier is None:
        _classifier = IncidentClassifier()
    return _classifier
