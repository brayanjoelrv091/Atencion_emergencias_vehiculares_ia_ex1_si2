"""
Bitácora de Auditoría — Registro de todas las acciones del sistema.

Requerimiento 4 — CU transversal a todos los módulos.
Registra: quién, cuándo, desde dónde, qué hizo.
"""

import logging
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import Session

from app.core.database import Base

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════
# MODELO
# ═══════════════════════════════════════════════════════════════════════

class Bitacora(Base):
    """Tabla de auditoría — registra todas las acciones del sistema."""

    __tablename__ = "bitacora"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, nullable=True, index=True)      # Null si aún no autenticado
    usuario_email = Column(String(255), nullable=True)
    rol = Column(String(20), nullable=True)
    accion = Column(String(255), nullable=False, index=True)     # Ej: "LOGIN_EXITOSO"
    descripcion = Column(Text, nullable=True)                    # Detalles legibles
    ip_origen = Column(String(60), nullable=True)
    modulo = Column(String(50), nullable=True)                   # Ej: "P1_USUARIOS"
    recurso_id = Column(Integer, nullable=True)                  # ID del recurso afectado
    resultado = Column(String(20), nullable=False, default="ok") # ok | error | advertencia
    registrado_en = Column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )


# ═══════════════════════════════════════════════════════════════════════
# SERVICIO
# ═══════════════════════════════════════════════════════════════════════

class BitacoraService:
    """Registra eventos de auditoría de forma silenciosa (no lanza excepciones)."""

    @staticmethod
    def registrar(
        db: Session,
        accion: str,
        *,
        usuario_id: int | None = None,
        usuario_email: str | None = None,
        rol: str | None = None,
        descripcion: str | None = None,
        ip_origen: str | None = None,
        modulo: str | None = None,
        recurso_id: int | None = None,
        resultado: str = "ok",
    ) -> None:
        """
        Inserta un registro en la bitácora.

        Nunca lanza excepciones para no interrumpir el flujo principal.
        """
        try:
            entrada = Bitacora(
                usuario_id=usuario_id,
                usuario_email=usuario_email,
                rol=rol,
                accion=accion,
                descripcion=descripcion,
                ip_origen=ip_origen,
                modulo=modulo,
                recurso_id=recurso_id,
                resultado=resultado,
                registrado_en=datetime.now(timezone.utc),
            )
            db.add(entrada)
            db.commit()
        except Exception as exc:  # pylint: disable=broad-except
            logger.error("[BITACORA] Error al registrar '%s': %s", accion, exc)
            db.rollback()

    # ── Métodos de conveniencia ──────────────────────────────────────

    @classmethod
    def login_exitoso(cls, db: Session, usuario_id: int, email: str, rol: str, ip: str | None) -> None:
        cls.registrar(db, "LOGIN_EXITOSO", usuario_id=usuario_id, usuario_email=email,
                      rol=rol, descripcion="Inicio de sesión exitoso", ip_origen=ip, modulo="P1_USUARIOS")

    @classmethod
    def login_fallido(cls, db: Session, email: str, intentos: int, ip: str | None) -> None:
        cls.registrar(db, "LOGIN_FALLIDO", usuario_email=email,
                      descripcion=f"Credenciales incorrectas. Intento #{intentos}",
                      ip_origen=ip, modulo="P1_USUARIOS", resultado="advertencia")

    @classmethod
    def cuenta_bloqueada(cls, db: Session, usuario_id: int, email: str, minutos: int | None, ip: str | None) -> None:
        desc = f"Cuenta bloqueada permanentemente" if minutos is None else f"Cuenta bloqueada {minutos} min"
        cls.registrar(db, "CUENTA_BLOQUEADA", usuario_id=usuario_id, usuario_email=email,
                      descripcion=desc, ip_origen=ip, modulo="P1_USUARIOS", resultado="advertencia")

    @classmethod
    def logout(cls, db: Session, usuario_id: int, email: str, ip: str | None) -> None:
        cls.registrar(db, "LOGOUT", usuario_id=usuario_id, usuario_email=email,
                      descripcion="Cierre de sesión", ip_origen=ip, modulo="P1_USUARIOS")

    @classmethod
    def registro_usuario(cls, db: Session, usuario_id: int, email: str, ip: str | None) -> None:
        cls.registrar(db, "REGISTRO_USUARIO", usuario_id=usuario_id, usuario_email=email,
                      descripcion="Nuevo usuario registrado", ip_origen=ip, modulo="P1_USUARIOS")

    @classmethod
    def recuperacion_password(cls, db: Session, email: str, ip: str | None) -> None:
        cls.registrar(db, "RECUPERACION_PASSWORD", usuario_email=email,
                      descripcion="Solicitud de recuperación de contraseña", ip_origen=ip,
                      modulo="P1_USUARIOS")

    @classmethod
    def password_restablecida(cls, db: Session, usuario_id: int, email: str, ip: str | None) -> None:
        cls.registrar(db, "PASSWORD_RESTABLECIDA", usuario_id=usuario_id, usuario_email=email,
                      descripcion="Contraseña restablecida exitosamente", ip_origen=ip,
                      modulo="P1_USUARIOS")

    @classmethod
    def cambio_password(cls, db: Session, usuario_id: int, email: str, ip: str | None) -> None:
        cls.registrar(db, "CAMBIO_PASSWORD", usuario_id=usuario_id, usuario_email=email,
                      descripcion="Contraseña cambiada desde el perfil", ip_origen=ip,
                      modulo="P1_USUARIOS")

    @classmethod
    def cambio_rol(cls, db: Session, admin_id: int, target_id: int, nuevo_rol: str, ip: str | None) -> None:
        cls.registrar(db, "CAMBIO_ROL", usuario_id=admin_id,
                      descripcion=f"Rol de usuario #{target_id} cambiado a '{nuevo_rol}'",
                      ip_origen=ip, modulo="P1_USUARIOS", recurso_id=target_id)

    @classmethod
    def incidente_reportado(cls, db: Session, usuario_id: int, incidente_id: int, ip: str | None) -> None:
        cls.registrar(db, "INCIDENTE_REPORTADO", usuario_id=usuario_id,
                      descripcion=f"Incidente #{incidente_id} reportado",
                      ip_origen=ip, modulo="P2_INCIDENTES", recurso_id=incidente_id)

    @classmethod
    def estado_solicitud_cambiado(cls, db: Session, usuario_id: int, solicitud_id: int, nuevo_estado: str, ip: str | None) -> None:
        cls.registrar(db, "ESTADO_SOLICITUD_CAMBIADO", usuario_id=usuario_id,
                      descripcion=f"Solicitud #{solicitud_id} → {nuevo_estado}",
                      ip_origen=ip, modulo="P3_TALLERES", recurso_id=solicitud_id)

    @classmethod
    def taller_asignado(cls, db: Session, incidente_id: int, taller_id: int, ip: str | None) -> None:
        cls.registrar(db, "TALLER_ASIGNADO",
                      descripcion=f"Taller #{taller_id} asignado al incidente #{incidente_id}",
                      ip_origen=ip, modulo="P4_ASIGNACION", recurso_id=incidente_id)
