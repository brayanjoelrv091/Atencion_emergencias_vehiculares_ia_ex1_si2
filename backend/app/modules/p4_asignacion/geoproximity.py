"""
P4 — Motor de Geoproximidad para Asignación Automática (CU14).

Implementa la fórmula de Haversine para calcular distancias entre
coordenadas GPS y un sistema de ranking multi-criterio.
"""

import math
from dataclasses import dataclass

# Radio de la Tierra en kilómetros
EARTH_RADIUS_KM = 6371.0

# Pesos del algoritmo de scoring
WEIGHT_DISTANCE = 0.40       # 40% distancia
WEIGHT_AVAILABILITY = 0.30   # 30% disponibilidad de técnicos
WEIGHT_SPECIALTY = 0.30      # 30% match de especialidad


@dataclass
class GeoPoint:
    """Punto geográfico con latitud y longitud."""
    latitud: float
    longitud: float


@dataclass
class WorkshopCandidate:
    """Candidato a asignación con sus métricas."""
    taller_id: int
    nombre: str
    distancia_km: float
    tecnicos_disponibles: int
    total_tecnicos: int
    especialidades: list[str]
    score_distancia: float = 0.0
    score_disponibilidad: float = 0.0
    score_especialidad: float = 0.0
    puntaje_total: float = 0.0


def haversine_distance(p1: GeoPoint, p2: GeoPoint) -> float:
    """
    Calcula la distancia en kilómetros entre dos puntos GPS
    usando la fórmula de Haversine.

    La fórmula de Haversine es más precisa que la distancia euclidiana
    para coordenadas geográficas porque considera la curvatura terrestre.

    Fórmula:
        a = sin²(Δlat/2) + cos(lat1) · cos(lat2) · sin²(Δlon/2)
        c = 2 · atan2(√a, √(1-a))
        d = R · c

    Args:
        p1: Punto de origen (ubicación del incidente).
        p2: Punto de destino (ubicación del taller).

    Returns:
        Distancia en kilómetros (precisión ~0.5%).
    """
    lat1 = math.radians(p1.latitud)
    lat2 = math.radians(p2.latitud)
    dlat = math.radians(p2.latitud - p1.latitud)
    dlon = math.radians(p2.longitud - p1.longitud)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS_KM * c


def _normalize_distance_score(distance_km: float, max_radius_km: float = 50.0) -> float:
    """
    Normaliza la distancia a un score de 0 a 1 (más cerca = más alto).
    Usa función exponencial inversa para penalizar distancias grandes.
    """
    if distance_km <= 0:
        return 1.0
    if distance_km >= max_radius_km:
        return 0.0
    return math.exp(-distance_km / (max_radius_km / 3))


def _availability_score(available: int, total: int) -> float:
    """Score de disponibilidad: ratio de técnicos disponibles."""
    if total == 0:
        return 0.0
    return available / total


def _normalize_text(text: str) -> str:
    """Elimina tildes y normaliza texto para matching robusto."""
    replacements = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ñ": "n"
    }
    result = text.lower().strip()
    for acc, plain in replacements.items():
        result = result.replace(acc, plain)
    return result


# Mapeo de nombres legacy/alternativos → categorías canónicas del sistema
_SPECIALTY_ALIASES: dict[str, str] = {
    "motor": "mecanico",
    "frenos": "mecanico",
    "transmision": "mecanico",
    "electricidad": "electrico",
    "bateria": "electrico",
    "carroceria": "carroceria",
    "pintura": "carroceria",
    "chapa": "carroceria",
    "llantas": "neumaticos",
    "neumaticos": "neumaticos",
    "emergencia": "emergencia_vial",
    "grua": "emergencia_vial",
    # Las categorías canónicas se mapean a sí mismas
    "mecanico": "mecanico",
    "electrico": "electrico",
    "emergencia_vial": "emergencia_vial",
}


def _specialty_score(
    workshop_specialties: list[str],
    incident_category: str | None,
) -> float:
    """
    Score de match de especialidad.

    Normaliza tildes y mapea nombres legacy (motor→mecanico,
    electricidad→electrico) para garantizar matching correcto.
    """
    if not incident_category or not workshop_specialties:
        return 0.5  # Neutral si no hay info

    # Normalizar la categoría del incidente
    normalized_category = _normalize_text(incident_category)
    canonical_category = _SPECIALTY_ALIASES.get(normalized_category, normalized_category)

    # Normalizar las especialidades del taller y buscar match
    for spec in workshop_specialties:
        normalized_spec = _normalize_text(spec)
        canonical_spec = _SPECIALTY_ALIASES.get(normalized_spec, normalized_spec)
        if canonical_spec == canonical_category:
            return 1.0  # Match perfecto

    return 0.2  # Sin match


def rank_workshops(
    incident_location: GeoPoint,
    incident_category: str | None,
    workshops: list[dict],
    max_radius_km: float = 50.0,
) -> list[WorkshopCandidate]:
    """
    Evalúa y rankea talleres candidatos para asignación.

    Algoritmo multi-criterio:
        Score = (0.40 × score_distancia) + (0.30 × score_disponibilidad) + (0.30 × score_especialidad)

    Args:
        incident_location: Coordenadas GPS del incidente.
        incident_category: Categoría del incidente (para match de especialidad).
        workshops: Lista de dicts con datos de talleres + técnicos.
        max_radius_km: Radio máximo de búsqueda.

    Returns:
        Lista de candidatos ordenados por puntaje (mayor a menor).
    """
    candidates: list[WorkshopCandidate] = []

    for ws in workshops:
        ws_location = GeoPoint(
            latitud=ws["latitud"],
            longitud=ws["longitud"],
        )
        distance = haversine_distance(incident_location, ws_location)

        # Filtrar por radio máximo
        if distance > max_radius_km:
            continue

        candidate = WorkshopCandidate(
            taller_id=ws["id"],
            nombre=ws["nombre"],
            distancia_km=round(distance, 2),
            tecnicos_disponibles=ws.get("tecnicos_disponibles", 0),
            total_tecnicos=ws.get("total_tecnicos", 0),
            especialidades=ws.get("especialidades", []),
        )

        # Calcular scores individuales
        candidate.score_distancia = _normalize_distance_score(distance, max_radius_km)
        candidate.score_disponibilidad = _availability_score(
            candidate.tecnicos_disponibles,
            candidate.total_tecnicos,
        )
        candidate.score_especialidad = _specialty_score(
            candidate.especialidades,
            incident_category,
        )

        # Score total ponderado
        candidate.puntaje_total = round(
            (WEIGHT_DISTANCE * candidate.score_distancia)
            + (WEIGHT_AVAILABILITY * candidate.score_disponibilidad)
            + (WEIGHT_SPECIALTY * candidate.score_especialidad),
            4,
        )

        candidates.append(candidate)

    # Ordenar por puntaje descendente
    candidates.sort(key=lambda c: c.puntaje_total, reverse=True)
    return candidates
