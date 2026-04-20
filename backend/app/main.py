"""
RutAIGeoProxi — API Backend (Monolito Modular).

Entry point que registra todos los módulos y configura el servidor.

Arquitectura:
    P1 · Usuarios y Seguridad     (CU1-CU6)   ✅ Implementado
    P2 · Gestión de Incidentes     (CU7-CU9)   ✅ Implementado
    P3 · Gestión de Talleres       (CU10-CU13)  ✅ Implementado
    P4 · Asignación y Logística    (CU14)       ✅ Implementado
    P5 · Pagos y Notificaciones    (CU15-CU18)  📋 Estructura lista
    P6 · Reportes                  (CU19-CU20)  📋 Estructura lista
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.core.security import get_password_hash

# ── Importar modelos de TODOS los módulos para que SQLAlchemy los registre ──
from app.modules.p1_usuarios.models import (  # noqa: F401
    TokenRecuperacion,
    TokenRevocado,
    Usuario,
    Vehiculo,
)
from app.shared.bitacora import Bitacora  # noqa: F401

from app.modules.p2_incidentes.models import (  # noqa: F401
    ClasificacionIncidente,
    Incidente,
    IncidenteMedia,
)
from app.modules.p3_talleres.models import (  # noqa: F401
    SolicitudServicio,
    Taller,
    Tecnico,
)
from app.modules.p4_asignacion.models import Asignacion  # noqa: F401

# ── Importar routers de módulos ──
from app.modules.p1_usuarios.routes import admin_router, audit_router, auth_router, profile_router
from app.modules.p2_incidentes.routes import router as incidents_router
from app.modules.p3_talleres.routes import router as workshops_router
from app.modules.p4_asignacion.routes import router as assignments_router
from app.modules.p5_pagos.routes import router as payments_router
from app.modules.p6_reportes.routes import router as reports_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════
# LIFESPAN (startup / shutdown)
# ═══════════════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Crea tablas y seed del admin al iniciar."""
    logger.info("🚀 Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Tablas creadas/verificadas")

    # Seed del administrador
    if settings.ADMIN_EMAIL and settings.ADMIN_PASSWORD:
        db = SessionLocal()
        try:
            if not db.query(Usuario).filter(Usuario.email == settings.ADMIN_EMAIL).first():
                db.add(
                    Usuario(
                        nombre="Administrador",
                        email=settings.ADMIN_EMAIL,
                        hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
                        rol="admin",
                        esta_activo=True,
                    )
                )
                db.commit()
                logger.info(f"👤 Admin seed creado: {settings.ADMIN_EMAIL}")
        finally:
            db.close()

    # Crear directorio de uploads si no existe
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    yield
    logger.info("🛑 Servidor detenido")


# ═══════════════════════════════════════════════════════════════════════
# APP
# ═══════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="RutAIGeoProxi API",
    description="Red de Asistencia Técnica Vehicular Inteligente — Monolito Modular",
    version="2.0.0",
    lifespan=lifespan,
)

# ── CORS ──
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Servir archivos estáticos (uploads locales) ──
if settings.UPLOAD_DIR.exists():
    app.mount("/uploads", StaticFiles(directory=str(settings.UPLOAD_DIR)), name="uploads")

# ── Registrar routers de módulos ──
# P1: Usuarios y Seguridad
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(profile_router)
app.include_router(audit_router)      # Req.4 — Bitácora
# P2: Incidentes
app.include_router(incidents_router)
# P3: Talleres
app.include_router(workshops_router)
# P4: Asignación
app.include_router(assignments_router)
# P5: Pagos (placeholder)
app.include_router(payments_router)
# P6: Reportes (placeholder)
app.include_router(reports_router)



# ── Root endpoint ──
@app.get("/", tags=["Sistema"])
def root():
    """Mapa de la API por ciclo y caso de uso."""
    return {
        "api": "RutAIGeoProxi",
        "version": "2.0.0",
        "arquitectura": "Monolito Modular",
        "modulos": {
            "P1_usuarios_seguridad": {
                "estado": "✅ Implementado",
                "CU1_inicio_sesion": "POST /auth/login [Bloqueo por capas Req.1]",
                "CU2_cierre_sesion": "POST /auth/logout",
                "CU3_registro": "POST /auth/register [Email Brevo Req.2]",
                "CU4a_recuperar_password": "POST /auth/forgot-password [Brevo SMTP Req.2]",
                "CU4b_reset_password": "POST /auth/reset-password [Regex Req.5]",
                "CU5_roles_permisos": "GET/POST /admin/users, PATCH /admin/users/{id}/role|permissions|unlock",
                "CU6_usuario_vehiculo": "GET/PATCH /me, POST /me/change-password, GET/POST/PATCH/DELETE /me/vehicles",
                "Req4_bitacora": "GET /audit/logs [Solo admin]",
            },
            "P2_incidentes": {
                "estado": "✅ Implementado",
                "CU7_reportar_incidente": "POST /incidents (multipart: fotos+audio+GPS)",
                "CU8_clasificacion_ia": "POST /incidents/{id}/classify (YOLOv8+Whisper+Reglas)",
                "CU9_ficha_incidente": "GET /incidents/{id}",
            },
            "P3_talleres": {
                "estado": "✅ Implementado",
                "CU10_registrar_taller": "POST /workshops + POST /workshops/{id}/technicians",
                "CU11_solicitudes": "GET /workshops/{id}/requests",
                "CU12_actualizar_estado": "PATCH /workshops/requests/{id}/status",
                "CU13_historial": "GET /workshops/{id}/history",
            },
            "P4_asignacion": {
                "estado": "✅ Implementado",
                "CU14_asignacion_automatica": "POST /assignments/auto/{incident_id} (Haversine+Multi-criterio)",
            },
            "P5_pagos": {"estado": "📋 Estructura lista — Ciclo 3"},
            "P6_reportes": {"estado": "📋 Estructura lista — Ciclo 3"},
        },
        "docs": "/docs",
    }
