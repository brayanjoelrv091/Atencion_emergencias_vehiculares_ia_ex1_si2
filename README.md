# RutAIGeoProxi — Sistema de Emergencias Vehiculares
Plataforma inteligente para emergencias vehiculares. Usa IA (YOLOv8 y Whisper) para clasificar incidentes mediante audio, imágenes y geolocalización, optimizando la asignación de talleres en tiempo real. 

Proyecto del 1er Parcial - Sistemas de Información 2 (UAGRM).

## 🚀 Despliegue Local (Para el Tribunal Evaluador)

Este proyecto emplea una arquitectura completa dividida en 3 capas:
1. **Backend:** Monolito Modular con FastAPI y SQLite (migrable a PostgreSQL).
2. **Frontend Web:** Angular 17 (Uso exclusivo de Administradores y Talleres) para el Panel de Control y gestión.
3. **Frontend Mobile:** Flutter (Uso exclusivo de Clientes) para reportar emergencias y hacer seguimiento.

---

### ⚙️ 1. Configurar el Backend (FastAPI)
1. Abrir la terminal en la carpeta `/backend`.
2. Crear un entorno virtual e instalar dependencias (Python 3.10+ recomendado):
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # En Windows
   # source venv/bin/activate # En Linux/Mac
   
   pip install -r requirements.txt
   ```
3. Renombrar el archivo `.env.example` a `.env` (ya viene preconfigurado para entorno local). 
   *Nota: Se debe reemplazar la clave `SMTP_PASSWORD` si se desean probar los envíos de correo mediante Brevo.*
4. Generar la base de datos y correr el **Seed Integral Demo**:
   ```bash
   python seed_demo_full.py
   ```
   *(Este script crea usuarios, talleres, vehículos, incidentes con IA simulada, asignaciones y pagos listos para mostrar al tribunal).*
5. Levantar el servidor:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   El backend estará disponible en `http://localhost:8000`. Puede ver la documentación interactiva en `http://localhost:8000/docs`.

### 💻 2. Configurar el Frontend (Angular)
1. Abrir otra terminal en la carpeta `/frontend`.
2. Instalar dependencias de Node.js:
   ```bash
   npm install
   ```
3. Levantar la Landing Page y el Dashboard:
   ```bash
   npm run start
   ```
4. Ingresar a `http://localhost:4200` e iniciar sesión.

### 📱 3. Configurar el Mobile (Flutter)
1. Abrir una terminal en la carpeta `/mobile`.
2. Instalar dependencias de Flutter:
   ```bash
   flutter pub get
   ```
3. Levantar la app en un emulador o dispositivo conectado:
   ```bash
   flutter run
   ```
   *(Si se prueba en un emulador Android local, el archivo `lib/config.dart` ya apunta por defecto a `10.0.2.2:8000`)*.

---

## 🔑 Credenciales para la Demo

Gracias al script `seed_demo_full.py`, puede ingresar a cualquiera de las plataformas (Web o Mobile) con los siguientes usuarios pre-cargados:

* **Admin:** `admin@ruta.com` | Contraseña: `Password123`
* **Cliente 1:** `cliente@ruta.com` | Contraseña: `Password123`
* **Cliente 2:** `cliente2@ruta.com` | Contraseña: `Password123`
* **Taller 1:** `taller@ruta.com` | Contraseña: `Password123`
* **Taller 2:** `taller2@ruta.com` | Contraseña: `Password123`

---

## 🧪 Pruebas Automatizadas (Testing)
El backend incluye una suite completa de pruebas unitarias y de integración que abarcan la autenticación, incidentes, talleres, asignaciones y notificaciones/pagos.

Para ejecutar los tests, desde la carpeta `/backend`:
```bash
pytest tests/ -v
```
