"""
P4 — Modelo de Asignación automática.

Tabla:
    - ``asignaciones`` → CU14
"""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text

from app.core.database import Base


class Asignacion(Base):
    """CU14 · Asignación automática de taller a un incidente."""

    __tablename__ = "asignaciones"

    id = Column(Integer, primary_key=True, index=True)
    incidente_id = Column(
        Integer,
        ForeignKey("incidentes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    taller_id = Column(
        Integer,
        ForeignKey("talleres.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    distancia_km = Column(Float, nullable=False)
    puntaje = Column(Float, nullable=False)      # Score final de asignación
    metodo = Column(String(50), nullable=False, default="haversine")
    razonamiento = Column(Text, nullable=True)  # Explicación del ranking
    asignado_en = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    # ── Relaciones (string refs para cross-module) ──
    from sqlalchemy.orm import relationship

    incidente = relationship("Incidente", back_populates="asignaciones")
    taller = relationship("Taller", back_populates="asignaciones")
