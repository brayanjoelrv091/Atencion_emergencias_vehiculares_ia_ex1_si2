from typing import Any

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.schemas.vehicle import VehicleOut

ALLOWED_ROLES = frozenset({"admin", "taller", "tecnico", "cliente"})


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str | None
    is_active: bool
    role: str
    permissions: dict[str, Any] | None

    model_config = {"from_attributes": True}


class MeResponse(UserOut):
    vehicles: list[VehicleOut] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class UserProfileUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    phone: str | None = Field(default=None, max_length=50)


class AdminUserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: str
    permissions: dict[str, Any] | None = None

    @field_validator("role")
    @classmethod
    def role_ok(cls, v: str) -> str:
        if v not in ALLOWED_ROLES:
            raise ValueError("Rol inválido")
        return v


class RoleUpdate(BaseModel):
    role: str

    @field_validator("role")
    @classmethod
    def role_ok(cls, v: str) -> str:
        if v not in ALLOWED_ROLES:
            raise ValueError("Rol inválido")
        return v


class PermissionsUpdate(BaseModel):
    permissions: dict[str, Any]
