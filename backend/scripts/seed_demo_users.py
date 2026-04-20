import sys
import os

# Add the parent directory to sys.path so we can import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.modules.p1_usuarios.models import Usuario
from app.core.security import get_password_hash

def seed_users():
    db: Session = SessionLocal()
    try:
        # Check if they exist to avoid unique constraint errors
        admin_email = "admin@ruta.com"
        taller_email = "taller@ruta.com"
        cliente_email = "cliente@ruta.com"
        
        # Hardcoded secure password matching Pydantic regex
        password = "Password123"
        hashed_pw = get_password_hash(password)
        
        users_added = 0
        
        if not db.query(Usuario).filter(Usuario.email == admin_email).first():
            db.add(Usuario(nombre="Super Admin", email=admin_email, hashed_password=hashed_pw, rol="admin", esta_activo=True))
            users_added += 1
            
        if not db.query(Usuario).filter(Usuario.email == taller_email).first():
            db.add(Usuario(nombre="Taller Mecanico Centro", email=taller_email, hashed_password=hashed_pw, rol="taller", esta_activo=True))
            users_added += 1
            
        if not db.query(Usuario).filter(Usuario.email == cliente_email).first():
            db.add(Usuario(nombre="Cliente VIP", email=cliente_email, hashed_password=hashed_pw, rol="cliente", esta_activo=True))
            users_added += 1

        db.commit()
        print(f"Exito: Se agregaron {users_added} usuarios demo con exito.")
        print("Credenciales generales:")
        print("Correos: admin@ruta.com | taller@ruta.com | cliente@ruta.com")
        print("Contrasena para todos: Password123")
        
    except Exception as e:
        print(f"Error insertando datos: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()
