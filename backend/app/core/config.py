"""
Configuración centralizada del monolito modular.
Lee variables de entorno (.env) y expone un singleton ``settings``.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # backend/


class Settings:
    # ── Base de datos ──────────────────────────────────────────────────
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # ── JWT ────────────────────────────────────────────────────────────
    SECRET_KEY: str = os.getenv("SECRET_KEY", "changeme")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120")
    )

    # ── Admin seed ─────────────────────────────────────────────────────
    ADMIN_EMAIL: str | None = os.getenv("ADMIN_EMAIL") or None
    ADMIN_PASSWORD: str | None = os.getenv("ADMIN_PASSWORD") or None

    # ── Debug ──────────────────────────────────────────────────────────
    DEBUG_RESET_TOKEN: bool = os.getenv("DEBUG_RESET_TOKEN", "").lower() in (
        "1",
        "true",
        "yes",
    )

    # ── CORS ───────────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = [
        o.strip()
        for o in (
            os.getenv(
                "CORS_ORIGINS",
                "http://localhost:3000,http://localhost:4200,"
                "http://localhost:5173,http://127.0.0.1:3000,"
                "http://127.0.0.1:4200,http://127.0.0.1:5173",
            )
        ).split(",")
        if o.strip()
    ]

    # ── Firebase Storage (opcional) ────────────────────────────────────
    FIREBASE_CREDENTIALS_PATH: str | None = (
        os.getenv("FIREBASE_CREDENTIALS_PATH") or None
    )
    FIREBASE_STORAGE_BUCKET: str | None = (
        os.getenv("FIREBASE_STORAGE_BUCKET") or None
    )

    # ── Almacenamiento local (fallback si Firebase no configurado) ─────
    UPLOAD_DIR: Path = BASE_DIR / "uploads"

    # ── IA — Clasificación de incidentes ───────────────────────────────
    YOLO_MODEL_PATH: str = os.getenv("YOLO_MODEL_PATH", "yolov8n.pt")
    WHISPER_MODEL_SIZE: str = os.getenv("WHISPER_MODEL_SIZE", "base")

    # ── SMTP (Brevo) ───────────────────────────────────────────────────
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp-relay.brevo.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str | None = os.getenv("SMTP_USER") or None
    SMTP_PASSWORD: str | None = os.getenv("SMTP_PASSWORD") or None
    FROM_EMAIL: str = os.getenv("FROM_EMAIL", "no-reply@rutaigeoproxi.com")

    @property
    def firebase_enabled(self) -> bool:
        return bool(self.FIREBASE_CREDENTIALS_PATH and self.FIREBASE_STORAGE_BUCKET)


settings = Settings()
