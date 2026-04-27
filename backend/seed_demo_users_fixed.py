import os
import sys
from dotenv import load_dotenv

# 1. ARREGLO DE RUTA: Le decimos explícitamente que "backend" es el directorio actual
directorio_actual = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, directorio_actual)
load_dotenv(os.path.join(directorio_actual, ".env"))

# Ahora los imports funcionarán como seda (¡CAMBIADO A SHARED!)
from sqlalchemy.orm import Session
from app.shared.database import SessionLocal, engine, Base
from app.modules.p1_usuarios.models import Usuario

# Importamos tu función de seguridad (¡CAMBIADO A SHARED!)
try:
    from app.shared.security import get_password_hash
except ImportError:
    print(
        "Aviso: Módulo de seguridad no encontrado. Usando contraseña en texto plano para la demo."
    )

    def get_password_hash(password):
        return password


def seed_users():
    # Aseguramos que la BD esté lista
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        admin_correo = "admin@ruta.com"
        taller_correo = "taller@ruta.com"
        cliente_correo = "cliente@ruta.com"

        password = "Password123"
        hashed_pw = get_password_hash(password)

        users_added = 0

        # 2. ARREGLO DE BD: Usamos email, hashed_password, rol y esta_activo (Tu esquema real)
        if not db.query(Usuario).filter(Usuario.email == admin_correo).first():
            db.add(
                Usuario(
                    nombre="Super Admin",
                    email=admin_correo,
                    hashed_password=hashed_pw,
                    rol="admin",
                    esta_activo=True,
                    intentos_fallidos=0,
                )
            )
            users_added += 1

        if not db.query(Usuario).filter(Usuario.email == taller_correo).first():
            db.add(
                Usuario(
                    nombre="Taller Mecanico Centro",
                    email=taller_correo,
                    hashed_password=hashed_pw,
                    rol="taller",
                    esta_activo=True,
                    intentos_fallidos=0,
                )
            )
            users_added += 1

        if not db.query(Usuario).filter(Usuario.email == cliente_correo).first():
            db.add(
                Usuario(
                    nombre="Cliente VIP",
                    email=cliente_correo,
                    hashed_password=hashed_pw,
                    rol="cliente",
                    esta_activo=True,
                    intentos_fallidos=0,
                )
            )
            users_added += 1

        db.commit()
        print(
            f"--- EXITO TOTAL: Se agregaron {users_added} usuarios demo a tu base de datos RutAIGeoProxi. ---"
        )
        print(
            "Correos para probar: admin@ruta.com | taller@ruta.com | cliente@ruta.com"
        )
        print("Contrasena para todos: Password123")

    except Exception as e:
        print(f"Error en la base de datos: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_users()
