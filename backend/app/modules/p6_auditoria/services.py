"""
P6 — Servicio de Auditoría (Bitácora).
"""

from fastapi import Request
from sqlalchemy.orm import Session
from app.modules.p6_auditoria.models import Bitacora


class AuditService:
    @staticmethod
    def log(
        db: Session,
        accion: str,
        request: Request | None = None,
        usuario_id: int | None = None,
        rol: str | None = None,
    ) -> None:
        """Registra un evento crítico en la bitácora."""
        
        ip_addr = "Desconocida"
        if request and request.client:
            ip_addr = request.client.host
            
        b = Bitacora(
            usuario_id=usuario_id,
            rol=rol,
            accion=accion,
            ip=ip_addr
        )
        db.add(b)
        db.commit()
