from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import admin_users, auth, profile
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.security import get_password_hash
from app.models import PasswordResetToken, RevokedToken, User, Vehicle  # noqa: F401 — registra tablas


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    if settings.ADMIN_EMAIL and settings.ADMIN_PASSWORD:
        db = SessionLocal()
        try:
            if not db.query(User).filter(User.email == settings.ADMIN_EMAIL).first():
                db.add(
                    User(
                        name="Administrador",
                        email=settings.ADMIN_EMAIL,
                        hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                        role="admin",
                        is_active=True,
                    )
                )
                db.commit()
        finally:
            db.close()
    yield


app = FastAPI(title="RutAIGeoProxi API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(admin_users.router)
app.include_router(profile.router)


@app.get("/")
def root():
    """Ciclo 1: CU-01 a CU-06 (auth, admin, perfil y vehículos del cliente)."""
    return {
        "message": "RutAIGeoProxi API",
        "ciclo_1": {
            "CU-01_inicio_sesion": "POST /auth/login",
            "CU-02_cierre_sesion": "POST /auth/logout",
            "CU-03_registro": "POST /auth/register | POST /admin/users",
            "CU-04_recuperar_password": "POST /auth/forgot-password | POST /auth/reset-password",
            "CU-05_roles_permisos": "GET /admin/users | PATCH /admin/users/{id}/role | .../permissions",
            "CU-06_usuario_vehiculo": "GET/PATCH /me | /me/vehicles",
        },
        "openapi": "/docs",
    }
