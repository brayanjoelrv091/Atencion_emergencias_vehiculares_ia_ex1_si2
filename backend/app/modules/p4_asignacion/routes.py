"""
P4 — Rutas de Asignación y Logística (CU14).

Endpoints:
    POST /assignments/auto/{incident_id}  → CU14 Asignación automática
    GET  /assignments/{incident_id}       → Ver asignación
"""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, get_db, require_roles
from app.modules.p1_usuarios.models import Usuario
from app.modules.p4_asignacion.schemas import (
    AssignmentOut,
    AutoAssignResponse,
    CandidateOut,
)
from app.modules.p4_asignacion.services import AssignmentService

router = APIRouter(prefix="/assignments", tags=["P4 · Asignación y Logística"])


@router.post(
    "/auto/{incident_id}",
    response_model=AutoAssignResponse,
    status_code=status.HTTP_201_CREATED,
    summary="CU14 · Asignación automática del taller más adecuado",
)
def auto_assign(
    incident_id: int,
    max_radius_km: float = Query(default=50.0, ge=1, le=500),
    db: Session = Depends(get_db),
    _current: Usuario = Depends(get_current_user),
):
    asignacion, candidates = AssignmentService.auto_assign(
        db, incident_id, max_radius_km
    )
    return AutoAssignResponse(
        asignacion=AssignmentOut.model_validate(asignacion),
        candidatos_evaluados=[
            CandidateOut(
                taller_id=c.taller_id,
                nombre=c.nombre,
                distancia_km=c.distancia_km,
                score_distancia=round(c.score_distancia, 4),
                score_disponibilidad=round(c.score_disponibilidad, 4),
                score_especialidad=round(c.score_especialidad, 4),
                puntaje_total=c.puntaje_total,
            )
            for c in candidates
        ],
        message=f"Taller '{candidates[0].nombre}' asignado ({candidates[0].distancia_km} km)",
    )


@router.get(
    "/{incident_id}",
    response_model=AssignmentOut,
    summary="Ver asignación de un incidente",
)
def get_assignment(
    incident_id: int,
    db: Session = Depends(get_db),
    _current: Usuario = Depends(get_current_user),
):
    return AssignmentService.get_assignment(db, incident_id)
