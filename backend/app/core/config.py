import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "changeme")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    ADMIN_EMAIL: str | None = os.getenv("ADMIN_EMAIL") or None
    ADMIN_PASSWORD: str | None = os.getenv("ADMIN_PASSWORD") or None
    DEBUG_RESET_TOKEN: bool = os.getenv("DEBUG_RESET_TOKEN", "").lower() in ("1", "true", "yes")
    # Orígenes permitidos para el frontend (coma-separado). Ej: http://localhost:5173
    CORS_ORIGINS: list[str] = [
        o.strip()
        for o in (
            os.getenv(
                "CORS_ORIGINS",
                "http://localhost:3000,http://localhost:5173,"
                "http://127.0.0.1:3000,http://127.0.0.1:5173",
            )
        ).split(",")
        if o.strip()
    ]


settings = Settings()
