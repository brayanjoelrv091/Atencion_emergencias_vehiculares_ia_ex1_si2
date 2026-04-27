"""
conftest.py — Fixtures compartidas para todos los tests de RutAIGeoProxi.

Usa SQLite en memoria para aislamiento total. Cada test recibe su
propia sesión de BD con tablas vacías.
"""

import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Forzar entorno de test ANTES de importar app
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-ci")
os.environ.setdefault("ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
os.environ.setdefault("DEBUG_RESET_TOKEN", "true")
os.environ.setdefault("ADMIN_EMAIL", "")
os.environ.setdefault("ADMIN_PASSWORD", "")
os.environ.setdefault("SMTP_SERVER", "")
os.environ.setdefault("SMTP_PORT", "587")
os.environ.setdefault("SMTP_USER", "")
os.environ.setdefault("SMTP_PASSWORD", "")
os.environ.setdefault("FROM_EMAIL", "test@test.com")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3000")
os.environ.setdefault("YOLO_MODEL_PATH", "yolov8n.pt")
os.environ.setdefault("WHISPER_MODEL_SIZE", "base")
os.environ.setdefault("FIREBASE_CREDENTIALS_PATH", "")
os.environ.setdefault("FIREBASE_STORAGE_BUCKET", "")

from app.shared.database import Base  # noqa: E402
from app.shared.deps import get_db  # noqa: E402
from app.main import app  # noqa: E402

SQLALCHEMY_TEST_URL = "sqlite:///:memory:"

engine_test = create_engine(
    SQLALCHEMY_TEST_URL,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest.fixture(scope="function")
def db():
    """Sesión de BD aislada por test — tablas creadas y destruidas."""
    Base.metadata.create_all(bind=engine_test)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine_test)


@pytest.fixture(scope="function")
def client(db):
    """TestClient con override de get_db apuntando a BD en memoria."""

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ── Helpers de usuario ─────────────────────────────────────────────────────

def _register(client: TestClient, email: str, nombre: str, rol: str = "cliente") -> dict:
    """Registra un usuario y retorna el body de respuesta."""
    r = client.post("/auth/register", json={
        "nombre": nombre,
        "email": email,
        "password": "Test1234!",
        "rol": rol,
    })
    assert r.status_code == 201, r.text
    return r.json()


def _login(client: TestClient, email: str, password: str = "Test1234!") -> str:
    """Inicia sesión y retorna el access_token."""
    r = client.post("/auth/login", json={"email": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def _auth_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def cliente_token(client):
    _register(client, "cliente@test.com", "Test Cliente")
    return _login(client, "cliente@test.com")


@pytest.fixture
def admin_token(client):
    """Crea usuario con rol admin directamente en BD (bypass registro público)."""
    from app.modules.p1_usuarios.models import Usuario
    from app.shared.security import get_password_hash

    # Usar el db del fixture pero a través del TestingSessionLocal
    session = TestingSessionLocal()
    Base.metadata.create_all(bind=engine_test)
    admin = Usuario(
        nombre="Admin Test",
        email="admin@test.com",
        hashed_password=get_password_hash("Admin1234!"),
        rol="admin",
        esta_activo=True,
        intentos_fallidos=0,
    )
    session.add(admin)
    session.commit()
    session.close()

    return _login(client, "admin@test.com", "Admin1234!")


@pytest.fixture
def taller_token(client):
    _register(client, "taller@test.com", "Taller Test", rol="taller")
    return _login(client, "taller@test.com")
