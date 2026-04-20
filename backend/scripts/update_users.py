import urllib.parse
from sqlalchemy import create_engine, text

# Hardcoded encode
pwd = urllib.parse.quote("RutA1_G3o_2026!#")
DB_URL = f"postgresql://postgres:{pwd}@localhost:5432/rutaigeoproxi_db"
engine = create_engine(DB_URL)

def upgrade_db():
    print("start")
    
    with engine.connect() as conn:
        try:
            conn.execute(text("ALTER TABLE usuarios ADD COLUMN intentos_fallidos INTEGER DEFAULT 0 NOT NULL;"))
            print("intentos_fallidos added.")
        except Exception as e:
            print("intentos_fallidos ya existe.")
            
        try:
            conn.execute(text("ALTER TABLE usuarios ADD COLUMN bloqueado_hasta TIMESTAMP WITH TIME ZONE;"))
            print("bloqueado_hasta added.")
        except Exception as e:
            print("bloqueado_hasta ya existe.")
            
        conn.commit()
        
    print("done")

if __name__ == "__main__":
    upgrade_db()
