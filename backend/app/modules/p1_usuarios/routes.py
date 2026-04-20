"""
P1 — Rutas (endpoints) de Usuarios y Seguridad.

Prefijos:
    /auth/*   → CU1, CU2, CU3, CU4
    /admin/*  → CU5
    /me/*     → CU6
    /audit/*  → Bitácora (solo admin)
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.deps import (
    get_current_user,
    get_db,
    get_token_credentials,
    require_roles,
)
from app.core.security import jwt_payload_safe
from app.modules.p1_usuarios.models import Usuario
from app.modules.p1_usuarios.schemas import (
    AdminUserCreate,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    MeResponse,
    PermissionsUpdate,
    ResetPasswordRequest,
    RoleUpdate,
    TokenResponse,
    UserCreate,
    UserOut,
    UserProfileUpdate,
    VehicleCreate,
    VehicleOut,
    VehicleUpdate,
)
from app.modules.p1_usuarios.services import AuthService, UserService, VehicleService
from app.shared.bitacora import Bitacora, BitacoraService

# ── Routers ────────────────────────────────────────────────────────────
auth_router   = APIRouter(prefix="/auth",  tags=["P1 · Autenticación"])
admin_router  = APIRouter(prefix="/admin", tags=["P1 · Administración"])
profile_router = APIRouter(prefix="/me",   tags=["P1 · Perfil y Vehículos"])
audit_router  = APIRouter(prefix="/audit", tags=["P1 · Bitácora de Auditoría"])

admin_dep = require_roles("admin")


def _get_ip(request: Request) -> str | None:
    """Extrae la IP real del cliente (soporta proxies)."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


# ═══════════════════════════════════════════════════════════════════════
# AUTH  (CU1 · Login, CU2 · Logout, CU3 · Registro, CU4 · Recuperar)
# ═══════════════════════════════════════════════════════════════════════

@auth_router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="CU3 · Registrar usuario",
)
def register(payload: UserCreate, request: Request, db: Session = Depends(get_db)):
    """Registro público. Envía email de bienvenida vía Brevo."""
    return AuthService.register(db, payload, ip=_get_ip(request))


@auth_router.post(
    "/login",
    response_model=TokenResponse,
    summary="CU1 · Iniciar sesión — con bloqueo por capas",
)
def login(payload: LoginRequest, request: Request, db: Session = Depends(get_db)):
    """
    Inicio de sesión con política de bloqueo progresivo:
    - Intento 3 → bloqueado 5 min
    - Intento 4 → bloqueado 15 min
    - Intento 5 → cuenta desactivada permanentemente + email notificación
    """
    return AuthService.login(db, payload, ip=_get_ip(request))


@auth_router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="CU2 · Cerrar sesión",
)
def logout(
    request: Request,
    db: Session = Depends(get_db),
    token: str = Depends(get_token_credentials),
):
    payload = jwt_payload_safe(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    AuthService.logout(db, token, payload, ip=_get_ip(request))


@auth_router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse,
    summary="CU4a · Solicitar recuperación — Email real via Brevo",
)
def forgot_password(
    payload: ForgotPasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    """Envía un email real con link de recuperación (token válido 1 hora)."""
    return AuthService.forgot_password(db, payload.email, ip=_get_ip(request))


@auth_router.post(
    "/reset-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="CU4b · Restablecer contraseña con token del email",
)
def reset_password(
    payload: ResetPasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    AuthService.reset_password(db, payload, ip=_get_ip(request))


# ═══════════════════════════════════════════════════════════════════════
# ADMIN  (CU5 · Roles, permisos y desbloqueos)
# ═══════════════════════════════════════════════════════════════════════

@admin_router.post(
    "/users",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="CU5 · Crear usuario (admin)",
)
def admin_create_user(
    payload: AdminUserCreate,
    db: Session = Depends(get_db),
    _current: Usuario = Depends(admin_dep),
):
    return UserService.admin_create(db, payload)


@admin_router.get(
    "/users",
    response_model=list[UserOut],
    summary="CU5 · Listar usuarios (admin)",
)
def admin_list_users(
    db: Session = Depends(get_db),
    _current: Usuario = Depends(admin_dep),
):
    return UserService.list_all(db)


@admin_router.patch(
    "/users/{user_id}/role",
    response_model=UserOut,
    summary="CU5 · Cambiar rol (admin)",
)
def admin_update_role(
    user_id: int,
    payload: RoleUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current: Usuario = Depends(admin_dep),
):
    return UserService.update_role(db, user_id, payload, current.id, ip=_get_ip(request))


@admin_router.patch(
    "/users/{user_id}/permissions",
    response_model=UserOut,
    summary="CU5 · Cambiar permisos (admin)",
)
def admin_update_permissions(
    user_id: int,
    payload: PermissionsUpdate,
    db: Session = Depends(get_db),
    _current: Usuario = Depends(admin_dep),
):
    return UserService.update_permissions(db, user_id, payload)


@admin_router.post(
    "/users/{user_id}/unlock",
    response_model=UserOut,
    summary="CU5 · Desbloquear cuenta ban permanente (admin)",
)
def admin_unlock_user(
    user_id: int,
    db: Session = Depends(get_db),
    current: Usuario = Depends(admin_dep),
):
    """Reactiva una cuenta bloqueada permanentemente por intentos fallidos."""
    return UserService.unlock_user(db, user_id, current.id)


# ═══════════════════════════════════════════════════════════════════════
# PERFIL  (CU6 · Datos de usuario y vehículo)
# ═══════════════════════════════════════════════════════════════════════

@profile_router.get("", response_model=MeResponse, summary="CU6 · Ver mi perfil")
def get_me(db: Session = Depends(get_db), current: Usuario = Depends(get_current_user)):
    return UserService.get_me(db, current.id)


@profile_router.patch("", response_model=MeResponse, summary="CU6 · Actualizar mi perfil")
def update_me(
    payload: UserProfileUpdate,
    db: Session = Depends(get_db),
    current: Usuario = Depends(get_current_user),
):
    return UserService.update_profile(db, current.id, payload)


@profile_router.post(
    "/change-password",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="CU6 · Cambiar contraseña desde perfil (requiere contraseña actual)",
)
def change_password(
    payload: ChangePasswordRequest,
    request: Request,
    db: Session = Depends(get_db),
    current: Usuario = Depends(get_current_user),
):
    """
    Req. 6 — Permite al usuario autenticado cambiar su propia contraseña.
    Exige la contraseña actual para evitar acceso no autorizado desde
    un dispositivo desbloqueado.
    """
    UserService.change_password(db, current.id, payload, ip=_get_ip(request))


@profile_router.get("/vehicles", response_model=list[VehicleOut], summary="CU6 · Listar vehículos")
def list_vehicles(db: Session = Depends(get_db), current: Usuario = Depends(get_current_user)):
    return VehicleService.list_by_user(db, current.id)


@profile_router.post(
    "/vehicles",
    response_model=VehicleOut,
    status_code=status.HTTP_201_CREATED,
    summary="CU6 · Registrar vehículo",
)
def create_vehicle(
    payload: VehicleCreate,
    db: Session = Depends(get_db),
    current: Usuario = Depends(get_current_user),
):
    if current.rol != "cliente":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Solo clientes pueden registrar vehículos")
    return VehicleService.create(db, current.id, payload)


@profile_router.patch("/vehicles/{vehicle_id}", response_model=VehicleOut, summary="CU6 · Actualizar vehículo")
def update_vehicle(
    vehicle_id: int,
    payload: VehicleUpdate,
    db: Session = Depends(get_db),
    current: Usuario = Depends(get_current_user),
):
    return VehicleService.update(db, vehicle_id, current.id, payload)


@profile_router.delete("/vehicles/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT, summary="CU6 · Eliminar vehículo")
def delete_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    current: Usuario = Depends(get_current_user),
):
    VehicleService.delete(db, vehicle_id, current.id)


# ═══════════════════════════════════════════════════════════════════════
# BITÁCORA  (Req. 4 · Solo admin)
# ═══════════════════════════════════════════════════════════════════════

from pydantic import BaseModel as _BM
from datetime import datetime as _dt

class BitacoraOut(_BM):
    id: int
    usuario_id: int | None
    usuario_email: str | None
    rol: str | None
    accion: str
    descripcion: str | None
    ip_origen: str | None
    modulo: str | None
    recurso_id: int | None
    resultado: str
    registrado_en: _dt
    model_config = {"from_attributes": True}


@audit_router.get(
    "/logs",
    response_model=list[BitacoraOut],
    summary="Req.4 · Ver bitácora de auditoría (admin)",
)
def get_audit_logs(
    limit: int = 100,
    modulo: str | None = None,
    db: Session = Depends(get_db),
    _current: Usuario = Depends(admin_dep),
):
    """Devuelve los últimos N registros de auditoría. Filtra por módulo si se indica."""
    q = db.query(Bitacora).order_by(Bitacora.registrado_en.desc())
    if modulo:
        q = q.filter(Bitacora.modulo == modulo.upper())
    return q.limit(limit).all()
