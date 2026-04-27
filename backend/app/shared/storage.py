"""
Servicio de almacenamiento de archivos.

Estrategia:
    1. Si Firebase Storage está configurado → sube a Firebase
    2. Si no → guarda en disco local (carpeta ``uploads/``)

Ambas estrategias retornan una URL accesible desde el frontend/mobile.
"""

import uuid
from pathlib import Path

from fastapi import UploadFile

from app.shared.config import settings

# Intentar cargar Firebase (opcional)
_firebase_bucket = None
if settings.firebase_enabled:
    try:
        import firebase_admin
        from firebase_admin import credentials, storage as fb_storage

        if not firebase_admin._apps:
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(
                cred, {"storageBucket": settings.FIREBASE_STORAGE_BUCKET}
            )
        _firebase_bucket = fb_storage.bucket()
    except Exception:
        _firebase_bucket = None


def _unique_filename(original: str) -> str:
    """Genera un nombre de archivo único preservando la extensión."""
    ext = Path(original).suffix or ".bin"
    return f"{uuid.uuid4().hex}{ext}"


async def upload_file(file: UploadFile, folder: str = "general") -> str:
    """
    Sube un archivo y retorna la URL pública.

    Args:
        file: Archivo recibido por FastAPI.
        folder: Subcarpeta lógica (ej: 'incidentes/fotos').

    Returns:
        URL de acceso al archivo.
    """
    filename = _unique_filename(file.filename or "archivo")
    content = await file.read()

    # ── Firebase Storage ───────────────────────────────────────────
    if _firebase_bucket is not None:
        blob_path = f"{folder}/{filename}"
        blob = _firebase_bucket.blob(blob_path)
        blob.upload_from_string(content, content_type=file.content_type)
        blob.make_public()
        return blob.public_url

    # ── Fallback: disco local ──────────────────────────────────────
    dest_dir = settings.UPLOAD_DIR / folder
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / filename
    dest.write_bytes(content)
    return f"/uploads/{folder}/{filename}"


async def upload_bytes(
    data: bytes,
    filename: str,
    content_type: str = "application/octet-stream",
    folder: str = "general",
) -> str:
    """Sube bytes crudos (útil para archivos procesados por IA)."""
    safe_name = _unique_filename(filename)

    if _firebase_bucket is not None:
        blob_path = f"{folder}/{safe_name}"
        blob = _firebase_bucket.blob(blob_path)
        blob.upload_from_string(data, content_type=content_type)
        blob.make_public()
        return blob.public_url

    dest_dir = settings.UPLOAD_DIR / folder
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / safe_name
    dest.write_bytes(data)
    return f"/uploads/{folder}/{safe_name}"
