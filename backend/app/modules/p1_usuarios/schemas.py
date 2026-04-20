"""
P1 — Schemas Pydantic para Usuarios y Seguridad.

Incluye:
  - Validación de contraseña con regex (Req. 5): min 8 chars, 1 mayúscula, 1 minúscula, 1 número.
  - ChangePasswordRequest para cambio desde el perfil (Req. 6).
  - Todos los campos obligatorios con Field() (Req. 3 — capa backend).
"""

import re
from typing import Any

from pydantic import BaseModel, EmailStr, Field, field_validator

# ── Roles válidos del sistema ──────────────────────────────────────────
ROLES_VALIDOS = frozenset({"admin", "taller", "cliente"})

# ── Regex de contraseña segura (Req. 5) ───────────────────────────────
# Mínimo 8 caracteres · al menos 1 mayúscula · 1 minúscula · 1 número
_PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$')

_PASSWORD_REGLAS = (
    "La contraseña debe tener mínimo 8 caracteres, "
    "al menos 1 mayúscula, 1 minúscula y 1 número."
)


def _validar_password(v: str) -> str:
    """Validor reutilizable para contraseñas con regex (Req. 5)."""
    if not _PASSWORD_REGEX.match(v):
        raise ValueError(_PASSWORD_REGLAS)
    return v


# ═══════════════════════════════════════════════════════════════════════
# AUTH  (CU1, CU2, CU4)
# ═══════════════════════════════════════════════════════════════════════

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, description="Contraseña del usuario")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=10)
    new_password: str = Field(min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def password_segura(cls, v: str) -> str:
        return _validar_password(v)


class ForgotPasswordResponse(BaseModel):
    message: str
    debug_token: str | None = None


# ── Cambio de contraseña desde el perfil (Req. 6) ─────────────────────

class ChangePasswordRequest(BaseModel):
    """CU6 — Cambio de contraseña autenticado (requiere contraseña actual)."""
    password_actual: str = Field(
        min_length=1,
        description="Contraseña actual del usuario (verificación de identidad)",
    )
    nueva_password: str = Field(
        min_length=8,
        max_length=128,
        description="Nueva contraseña (mín. 8 chars, 1 mayúscula, 1 minúscula, 1 número)",
    )

    @field_validator("nueva_password")
    @classmethod
    def password_segura(cls, v: str) -> str:
        return _validar_password(v)


# ═══════════════════════════════════════════════════════════════════════
# VEHÍCULOS  (CU6)
# ═══════════════════════════════════════════════════════════════════════

class VehicleCreate(BaseModel):
    marca: str = Field(min_length=1, max_length=100)
    modelo: str = Field(min_length=1, max_length=100)
    placa: str = Field(min_length=1, max_length=20)
    anio: int | None = Field(default=None, ge=1900, le=2100)
    color: str | None = Field(default=None, max_length=50)


class VehicleUpdate(BaseModel):
    marca: str | None = Field(default=None, min_length=1, max_length=100)
    modelo: str | None = Field(default=None, min_length=1, max_length=100)
    placa: str | None = Field(default=None, min_length=1, max_length=20)
    anio: int | None = Field(default=None, ge=1900, le=2100)
    color: str | None = Field(default=None, max_length=50)


class VehicleOut(BaseModel):
    id: int
    usuario_id: int
    marca: str
    modelo: str
    placa: str
    anio: int | None
    color: str | None

    model_config = {"from_attributes": True}


# ═══════════════════════════════════════════════════════════════════════
# USUARIOS  (CU3, CU5, CU6)
# ═══════════════════════════════════════════════════════════════════════

class UserCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=200)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_segura(cls, v: str) -> str:
        return _validar_password(v)


class UserOut(BaseModel):
    id: int
    nombre: str
    email: EmailStr
    telefono: str | None
    esta_activo: bool
    rol: str
    permisos: dict[str, Any] | None

    model_config = {"from_attributes": True}


class MeResponse(UserOut):
    vehiculos: list[VehicleOut] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class UserProfileUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=200)
    telefono: str | None = Field(default=None, max_length=50)


class AdminUserCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=200)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    rol: str
    permisos: dict[str, Any] | None = None

    @field_validator("password")
    @classmethod
    def password_segura(cls, v: str) -> str:
        return _validar_password(v)

    @field_validator("rol")
    @classmethod
    def rol_valido(cls, v: str) -> str:
        if v not in ROLES_VALIDOS:
            raise ValueError(f"Rol inválido. Válidos: {', '.join(sorted(ROLES_VALIDOS))}")
        return v


class RoleUpdate(BaseModel):
    rol: str

    @field_validator("rol")
    @classmethod
    def rol_valido(cls, v: str) -> str:
        if v not in ROLES_VALIDOS:
            raise ValueError(f"Rol inválido. Válidos: {', '.join(sorted(ROLES_VALIDOS))}")
        return v


class PermissionsUpdate(BaseModel):
    permisos: dict[str, Any]
