# Atencion_emergencias_vehiculares_ia_ex1_si2
Plataforma inteligente para emergencias vehiculares. Usa IA para clasificar incidentes mediante audio, imágenes y geolocalización, optimizando la asignación de talleres. Proyecto del 1er Parcial - Sistemas de Información 2 (UAGRM).

## 🚀 Despliegue Local (Para el Tribunal Evaluador)

Este proyecto emplea un **Monolito Modular** en el Backend (FastAPI / SQLite) y **Angular 17** en el Frontend. 

### ⚙️ 1. Configurar el Backend (FastAPI)
1. Abrir la terminal en la carpeta `/backend`.
2. Crear un entorno virtual e instalar dependencias (asegúrate de tener Python 3.10+):
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. Renombrar el archivo `.env.example` a `.env`. (Ya viene preconfigurado con SQLite).
4. Generar la base de datos y los usuarios de prueba:
   ```bash
   python scripts/seed_demo_users_fixed.py
   ```
5. Levantar el servidor:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

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
4. Ingresar a `http://localhost:4200` e iniciar sesión interactiva con las credenciales demo inyectadas por el Backend:
   * **Admin:** admin@ruta.com | Contraseña: Password123
   * **Taller:** taller@ruta.com | Contraseña: Password123
   * **Cliente:** cliente@ruta.com | Contraseña: Password123
