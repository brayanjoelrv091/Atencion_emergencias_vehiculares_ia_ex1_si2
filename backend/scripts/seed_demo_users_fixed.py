import os
from dotenv import load_dotenv

# Load env before importing app
load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env')))

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.modules.p1_usuarios.models import Usuario
from app.core.security import get_password_hash

def seed_users():
    # Asegúrate de que las tablas existan (ideal para SQLite)
    import app.modules.p1_usuarios.models
    import app.modules.p2_incidentes.models
    import app.modules.p3_talleres.models
    import app.modules.p4_asignacion.models
    import app.modules.p6_auditoria.models
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        admin_email = "admin@ruta.com"
        taller_email = "taller@ruta.com"
        cliente_email = "cliente@ruta.com"
        
        password = "Password123"
        hashed_pw = get_password_hash(password)
        
        users_added = 0
        
        if not db.query(Usuario).filter(Usuario.email == admin_email).first():
            db.add(Usuario(nombre="Super Admin", email=admin_email, hashed_password=hashed_pw, rol="admin", esta_activo=True, intentos_fallidos=0))
            users_added += 1
            
        if not db.query(Usuario).filter(Usuario.email == taller_email).first():
            db.add(Usuario(nombre="Taller Mecanico Centro", email=taller_email, hashed_password=hashed_pw, rol="taller", esta_activo=True, intentos_fallidos=0))
            users_added += 1
            
        if not db.query(Usuario).filter(Usuario.email == cliente_email).first():
            db.add(Usuario(nombre="Cliente VIP", email=cliente_email, hashed_password=hashed_pw, rol="cliente", esta_activo=True, intentos_fallidos=0))
            users_added += 1

        db.commit()
        print(f"OK: Se agregaron {users_added} usuarios demo con exito.")
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_users()
