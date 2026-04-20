"""P5 — Rutas de Pagos y Notificaciones (placeholder Ciclo 3)."""

from fastapi import APIRouter

router = APIRouter(prefix="/payments", tags=["P5 · Pagos y Notificaciones (próximamente)"])


@router.get("/status")
def payments_status():
    return {"module": "P5 — Pagos y Notificaciones", "status": "En desarrollo — Ciclo 3"}
