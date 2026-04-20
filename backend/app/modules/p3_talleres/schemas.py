"""
P3 — Schemas Pydantic para Talleres.
"""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# ═══════════════════════════════════════════════════════════════════════
# TALLER  (CU10)
# ═══════════════════════════════════════════════════════════════════════

class WorkshopCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=200)
    direccion: str = Field(min_length=5, max_length=500)
    latitud: float = Field(ge=-90, le=90)
    longitud: float = Field(ge=-180, le=180)
    telefono: str | None = Field(default=None, max_length=50)
    email: EmailStr | None = None
    especialidades: list[str] | None = None


class WorkshopOut(BaseModel):
    id: int
    usuario_propietario_id: int
    nombre: str
    direccion: str
    latitud: float
    longitud: float
    telefono: str | None
    email: str | None
    especialidades: list[str] | None
    esta_activo: bool
    calificacion_promedio: float
    creado_en: datetime

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════
# TÉCNICO  (CU10)
# ═══════════════════════════════════════════════════════════════════════

class TechnicianCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=200)
    telefono: str | None = Field(default=None, max_length=50)
    especialidad: str | None = Field(default=None, max_length=50)
    latitud: float | None = Field(default=None, ge=-90, le=90)
    longitud: float | None = Field(default=None, ge=-180, le=180)


class TechnicianOut(BaseModel):
    id: int
    taller_id: int
    nombre: str
    telefono: str | None
    especialidad: str | None
    esta_disponible: bool
    latitud: float | None
    longitud: float | None

    model_config = {"from_attributes": True}


class TechnicianAvailabilityUpdate(BaseModel):
    esta_disponible: bool


# ═══════════════════════════════════════════════════════════════════════
# SOLICITUD DE SERVICIO  (CU11, CU12, CU13)
# ═══════════════════════════════════════════════════════════════════════

ESTADOS_VALIDOS = frozenset({"pendiente", "proceso", "atendido", "cancelado"})

# Transiciones válidas de estado
TRANSICIONES_VALIDAS: dict[str, set[str]] = {
    "pendiente": {"proceso", "cancelado"},
    "proceso": {"atendido", "cancelado"},
    "atendido": set(),      # estado final
    "cancelado": set(),     # estado final
}


class ServiceRequestOut(BaseModel):
    id: int
    incidente_id: int
    taller_id: int
    tecnico_id: int | None
    estado: str
    notas: str | None
    creado_en: datetime
    actualizado_en: datetime | None

    model_config = {"from_attributes": True}


class ServiceStatusUpdate(BaseModel):
    estado: str
    notas: str | None = None
    tecnico_id: int | None = None

    @classmethod
    def validate_estado(cls, v: str) -> str:
        if v not in ESTADOS_VALIDOS:
            raise ValueError(f"Estado inválido. Válidos: {', '.join(sorted(ESTADOS_VALIDOS))}")
        return v


class ServiceHistoryOut(BaseModel):
    id: int
    incidente_id: int
    taller_id: int
    tecnico_id: int | None
    estado: str
    notas: str | None
    creado_en: datetime
    actualizado_en: datetime | None
    # Info del incidente embebida
    titulo_incidente: str | None = None
    categoria_incidente: str | None = None
    severidad_incidente: str | None = None

    model_config = {"from_attributes": True}
