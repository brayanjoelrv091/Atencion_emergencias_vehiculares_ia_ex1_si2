"""
P1 — Capa de servicios (lógica de negocio) de Usuarios y Seguridad.

Implementa:
  - Req. 1: Bloqueo de contraseña por capas (5min → 15min → permanente)
  - Req. 2: Recuperación via Brevo SMTP (email real)
  - Req. 3: Validaciones Pydantic (Field min_length, regex)
  - Req. 4: Bitácora de auditoría en todas las acciones
  - Req. 5: Validación regex contraseña (en schemas.py)
  - Req. 6: Cambio de contraseña desde el perfil (requiere password actual)
"""

from datetime import datetime, timedelta, timezone
from threading import Thread

from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.config import settings
from app.core.email import EmailService
from app.core.security import (
    create_access_token,
    generate_reset_token,
    get_password_hash,
    hash_reset_token,
    verify_password,
)
from app.modules.p1_usuarios.models import (
    TokenRecuperacion,
    TokenRevocado,
    Usuario,
    Vehiculo,
)
from app.modules.p1_usuarios.schemas import (
    AdminUserCreate,
    ChangePasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    PermissionsUpdate,
    ResetPasswordRequest,
    RoleUpdate,
    TokenResponse,
    UserCreate,
    UserProfileUpdate,
    VehicleCreate,
    VehicleUpdate,
)
from app.shared.bitacora import BitacoraService

# ── Política de bloqueo por capas (Req. 1) ───────────────────────────
_LOCKOUT_POLICY = {
    3: timedelta(minutes=5),   # 3er intento  → 5 min
    4: timedelta(minutes=15),  # 4to intento  → 15 min
}
_MAX_INTENTOS_PERMANENTE = 5   # 5to intento  → desactivación permanente


def _send_email_async(fn, *args) -> None:
    """Envía email en background para no bloquear la respuesta HTTP."""
    Thread(target=fn, args=args, daemon=True).start()


# ═══════════════════════════════════════════════════════════════════════
# AUTH SERVICE  (CU1, CU2, CU3, CU4)
# ═══════════════════════════════════════════════════════════════════════

class AuthService:
    """Servicio de autenticación y registro."""

    @staticmethod
    def register(db: Session, payload: UserCreate, ip: str | None = None) -> Usuario:
        """CU3 — Registrar usuario con email de bienvenida y auditoría."""
        if db.query(Usuario).filter(Usuario.email == payload.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo ya está registrado",
            )
        user = Usuario(
            nombre=payload.nombre,
            email=payload.email,
            hashed_password=get_password_hash(payload.password),
            rol="cliente",
            esta_activo=True,
            intentos_fallidos=0,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        # Bitácora
        BitacoraService.registro_usuario(db, user.id, user.email, ip)

        # Email de bienvenida (async)
        _send_email_async(EmailService.send_welcome, user.email, user.nombre)

        return user

    @staticmethod
    def login(db: Session, payload: LoginRequest, ip: str | None = None) -> TokenResponse:
        """
        CU1 — Inicio de sesión con bloqueo por capas (Req. 1).

        Política:
          Intento 1-2 → Error simple
          Intento 3   → Bloqueado 5 minutos
          Intento 4   → Bloqueado 15 minutos
          Intento 5+  → Cuenta desactivada permanentemente
        """
        now = datetime.now(timezone.utc)
        user = db.query(Usuario).filter(Usuario.email == payload.email).first()

        # ── Cuenta no existe ─────────────────────────────────────────
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
            )

        # ── Cuenta desactivada permanentemente ───────────────────────
        if not user.esta_activo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    "Tu cuenta ha sido bloqueada permanentemente por exceder el límite "
                    "de intentos. Contacta a soporte@rutaigeoproxi.com o a tu administrador."
                ),
            )

        # ── Bloqueo temporal vigente ── ───────────────────────────────
        if user.bloqueado_hasta and user.bloqueado_hasta > now:
            minutos_restantes = max(1, int((user.bloqueado_hasta - now).total_seconds() / 60) + 1)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=(
                    f"Cuenta bloqueada temporalmente. "
                    f"Intenta de nuevo en {minutos_restantes} minuto(s)."
                ),
            )

        # ── Verificar contraseña ─────────────────────────────────────
        if not verify_password(payload.password, user.hashed_password):
            user.intentos_fallidos = (user.intentos_fallidos or 0) + 1
            intentos = user.intentos_fallidos

            BitacoraService.login_fallido(db, user.email, intentos, ip)

            # Aplicar política de bloqueo
            if intentos >= _MAX_INTENTOS_PERMANENTE:
                # Bloqueo permanente → desactivar cuenta
                user.esta_activo = False
                user.bloqueado_hasta = None
                db.commit()
                BitacoraService.cuenta_bloqueada(db, user.id, user.email, None, ip)
                _send_email_async(EmailService.send_account_locked, user.email, user.nombre)
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        "Límite de intentos excedido. Tu cuenta ha sido bloqueada permanentemente. "
                        "Contacta a soporte@rutaigeoproxi.com o a tu administrador para desbloquearla."
                    ),
                )
            elif intentos in _LOCKOUT_POLICY:
                minutos = int(_LOCKOUT_POLICY[intentos].total_seconds() / 60)
                user.bloqueado_hasta = now + _LOCKOUT_POLICY[intentos]
                db.commit()
                BitacoraService.cuenta_bloqueada(db, user.id, user.email, minutos, ip)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=(
                        f"Demasiados intentos. Tu cuenta ha sido bloqueada por "
                        f"{minutos} minutos por seguridad."
                    ),
                )
            else:
                db.commit()
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Credenciales incorrectas",
                )

        # ── Login exitoso: resetear contadores ───────────────────────
        user.intentos_fallidos = 0
        user.bloqueado_hasta = None
        db.commit()

        token, _jti, expire = create_access_token(user_id=user.id, role=user.rol)
        expires_in = max(0, int((expire - now).total_seconds()))

        BitacoraService.login_exitoso(db, user.id, user.email, user.rol, ip)

        return TokenResponse(access_token=token, expires_in=expires_in)

    @staticmethod
    def logout(db: Session, token: str, payload: dict, ip: str | None = None) -> None:
        """CU2 — Cierre de sesión (revoca JWT)."""
        jti = payload.get("jti")
        exp_ts = payload.get("exp")
        if not jti or exp_ts is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
        if db.query(TokenRevocado).filter(TokenRevocado.jti == jti).first():
            return
        expires_at = datetime.fromtimestamp(int(exp_ts), tz=timezone.utc)
        db.add(TokenRevocado(
            jti=jti,
            expira_en=expires_at,
            revocado_en=datetime.now(timezone.utc),
        ))
        db.commit()

        user_id = payload.get("sub")
        email = payload.get("email", "")
        BitacoraService.logout(db, int(user_id) if user_id else None, email, ip)

    @staticmethod
    def forgot_password(db: Session, email: str, ip: str | None = None) -> ForgotPasswordResponse:
        """CU4a — Solicitar recuperación; envía email real via Brevo (Req. 2)."""
        msg = "Si el correo existe en el sistema, recibirás instrucciones para restablecer la contraseña."
        user = db.query(Usuario).filter(Usuario.email == email).first()

        if not user:
            # Respuesta ambigua por seguridad (anti-enumeration)
            return ForgotPasswordResponse(message=msg, debug_token=None)

        raw = generate_reset_token()
        th = hash_reset_token(raw)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        db.add(TokenRecuperacion(
            usuario_id=user.id,
            token_hash=th,
            expira_en=expires_at,
        ))
        db.commit()

        BitacoraService.recuperacion_password(db, user.email, ip)

        # Email real via Brevo (async en background)
        _send_email_async(EmailService.send_reset_password, user.email, user.nombre, raw)

        # Solo exponer token en modo debug
        debug = raw if settings.DEBUG_RESET_TOKEN else None
        return ForgotPasswordResponse(message=msg, debug_token=debug)

    @staticmethod
    def reset_password(db: Session, payload: ResetPasswordRequest, ip: str | None = None) -> None:
        """CU4b — Restablecer contraseña con token del correo."""
        th = hash_reset_token(payload.token)
        now = datetime.now(timezone.utc)
        row = (
            db.query(TokenRecuperacion)
            .filter(
                TokenRecuperacion.token_hash == th,
                TokenRecuperacion.usado_en.is_(None),
                TokenRecuperacion.expira_en > now,
            )
            .first()
        )
        if not row:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido o expirado",
            )
        user = db.query(Usuario).filter(Usuario.id == row.usuario_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido")

        user.hashed_password = get_password_hash(payload.new_password)
        # Resetear bloqueo si estaba bloqueado temporalmente
        user.intentos_fallidos = 0
        user.bloqueado_hasta = None
        # Si estaba permanentemente desactivado, el admin debe reactivarlo manualmente
        row.usado_en = now
        db.commit()

        BitacoraService.password_restablecida(db, user.id, user.email, ip)


# ═══════════════════════════════════════════════════════════════════════
# USER SERVICE  (CU5, CU6)
# ═══════════════════════════════════════════════════════════════════════

class UserService:
    """Servicio de gestión de usuarios (perfil y admin)."""

    @staticmethod
    def get_me(db: Session, user_id: int) -> Usuario:
        """CU6 — Obtener perfil con vehículos."""
        user = (
            db.query(Usuario)
            .options(joinedload(Usuario.vehiculos))
            .filter(Usuario.id == user_id)
            .first()
        )
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
        return user

    @staticmethod
    def update_profile(db: Session, user_id: int, payload: UserProfileUpdate) -> Usuario:
        """CU6 — Actualizar nombre/teléfono del perfil."""
        user = (
            db.query(Usuario)
            .options(joinedload(Usuario.vehiculos))
            .filter(Usuario.id == user_id)
            .first()
        )
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
        data = payload.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(user, k, v)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def change_password(
        db: Session, user_id: int, payload: ChangePasswordRequest, ip: str | None = None
    ) -> None:
        """
        Req. 6 — Cambiar contraseña desde el perfil autenticado.

        Requiere contraseña actual para evitar que alguien que
        agarra el teléfono desbloqueado cambie la clave.
        """
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")

        if not verify_password(payload.password_actual, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña actual es incorrecta",
            )

        user.hashed_password = get_password_hash(payload.nueva_password)
        db.commit()

        BitacoraService.cambio_password(db, user.id, user.email, ip)

    @staticmethod
    def list_all(db: Session) -> list[Usuario]:
        """CU5 — Listar todos los usuarios (admin)."""
        return db.query(Usuario).order_by(Usuario.id).all()

    @staticmethod
    def admin_create(db: Session, payload: AdminUserCreate) -> Usuario:
        """CU5 — Crear usuario con rol específico (admin)."""
        if db.query(Usuario).filter(Usuario.email == payload.email).first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo ya está registrado",
            )
        user = Usuario(
            nombre=payload.nombre,
            email=payload.email,
            hashed_password=get_password_hash(payload.password),
            rol=payload.rol,
            esta_activo=True,
            permisos=payload.permisos,
            intentos_fallidos=0,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_role(db: Session, user_id: int, payload: RoleUpdate, admin_id: int, ip: str | None = None) -> Usuario:
        """CU5 — Cambiar rol de un usuario (admin)."""
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
        if user.id == admin_id and payload.rol != "admin":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No puedes quitarte el rol de administrador a ti mismo",
            )
        user.rol = payload.rol
        db.commit()
        db.refresh(user)
        BitacoraService.cambio_rol(db, admin_id, user_id, payload.rol, ip)
        return user

    @staticmethod
    def unlock_user(db: Session, user_id: int, admin_id: int) -> Usuario:
        """CU5 — Desbloquear cuenta ban permanente (admin)."""
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
        user.esta_activo = True
        user.intentos_fallidos = 0
        user.bloqueado_hasta = None
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def update_permissions(db: Session, user_id: int, payload: PermissionsUpdate) -> Usuario:
        """CU5 — Actualizar permisos de un usuario (admin)."""
        user = db.query(Usuario).filter(Usuario.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
        user.permisos = payload.permisos
        db.commit()
        db.refresh(user)
        return user


# ═══════════════════════════════════════════════════════════════════════
# VEHICLE SERVICE  (CU6)
# ═══════════════════════════════════════════════════════════════════════

class VehicleService:
    """Servicio de gestión de vehículos del cliente."""

    @staticmethod
    def list_by_user(db: Session, user_id: int) -> list[Vehiculo]:
        return (
            db.query(Vehiculo)
            .filter(Vehiculo.usuario_id == user_id)
            .order_by(Vehiculo.id)
            .all()
        )

    @staticmethod
    def create(db: Session, user_id: int, payload: VehicleCreate) -> Vehiculo:
        v = Vehiculo(
            usuario_id=user_id,
            marca=payload.marca,
            modelo=payload.modelo,
            placa=payload.placa.strip().upper(),
            anio=payload.anio,
            color=payload.color,
        )
        db.add(v)
        db.commit()
        db.refresh(v)
        return v

    @staticmethod
    def update(db: Session, vehicle_id: int, user_id: int, payload: VehicleUpdate) -> Vehiculo:
        v = (
            db.query(Vehiculo)
            .filter(Vehiculo.id == vehicle_id, Vehiculo.usuario_id == user_id)
            .first()
        )
        if not v:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")
        data = payload.model_dump(exclude_unset=True)
        if "placa" in data and data["placa"] is not None:
            data["placa"] = data["placa"].strip().upper()
        for k, val in data.items():
            setattr(v, k, val)
        db.commit()
        db.refresh(v)
        return v

    @staticmethod
    def delete(db: Session, vehicle_id: int, user_id: int) -> None:
        v = (
            db.query(Vehiculo)
            .filter(Vehiculo.id == vehicle_id, Vehiculo.usuario_id == user_id)
            .first()
        )
        if not v:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehículo no encontrado")
        db.delete(v)
        db.commit()
