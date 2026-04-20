"""P6 — Rutas de Reportes (placeholder Ciclo 3)."""

from fastapi import APIRouter

router = APIRouter(prefix="/reports", tags=["P6 · Reportes (próximamente)"])


@router.get("/status")
def reports_status():
    return {"module": "P6 — Reportes", "status": "En desarrollo — Ciclo 3"}
