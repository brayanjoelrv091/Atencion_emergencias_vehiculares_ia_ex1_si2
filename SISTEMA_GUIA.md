# ⚡ Guía del Ecosistema RutAIGeoProxi (SaaS Premium)

Esta plataforma es un sistema **SaaS** modular de misión crítica que supera los requerimientos base del Examen 1 de Sistemas de Información 2.

## 👥 Credenciales de Acceso (Tribunal Evaluador)

| Rol | Correo | Contraseña | Valor Agregado en Seguridad |
| :--- | :--- | :--- | :--- |
| **Administrador** | `admin@ruta.com` | `Password123` | **RBAC Shield**: Único capaz de ver auditorías y reportes financieros. |
| **Dueño de Taller** | `taller@ruta.com` | `Password123` | **Multi-tenant**: Gestión privada de sus propios técnicos y órdenes. |
| **Cliente / Conductor**| `cliente@ruta.com` | `Password123` | **Privacidad de Datos**: Solo ve sus propios vehículos e incidentes. |

---

## 🛰️ Flujo del Sistema Detallado

### 1. Marketing e Introducción (Landing Page)
- **Criterio Propio**: Diseño premium con Glassmorphism y Tailwind CSS que "vende" el producto a talleres y clientes.

### 2. Reporte de Emergencia Multimodal (CU7)
- El usuario reporta con **GPS + Foto + Audio**.
- **Bonus**: Sincronización inmediata con el Backend para procesamiento paralelo.

### 3. Inteligencia Artificial de Consenso (IA Pro) - **SUPERACIÓN DE ALCANCE**
A diferencia de sistemas básicos, RutAIGeoProxi usa:
- **YOLOv8**: Clasificación visual de daños (Rueda, Choque, Motor).
- **OpenAI Whisper**: Transcripción de audio del conductor.
- **Motor de Reglas**: Ponderación de keywords.
- **Resultado**: La IA asigna una **Severidad** (Leve, Moderado, Grave, Crítico) basada en el consenso de estas 3 fuentes.

### 4. Asignación Geo-Inteligente (P4)
- Algoritmo **Haversine** optimizado para evitar consultas N+1 en la base de datos.
- Filtra por: Radio de cercanía, disponibilidad operativa del taller y especialidad técnica.

### 5. Ciclo de Negocio y Pagos (SaaS)
- **Comisión del 10%**: Automatizada en cada pago procesado.
- **Trazabilidad**: Cada centavo es registrado en el módulo de Auditoría (P6).

---

## 🏗️ Stack Tecnológico Profesional
- **Backend**: FastAPI (Python) - Estructura modular escalable.
- **Frontend**: Angular + Vanilla CSS/Tailwind - Dashboard dinámico y reactivo.
- **Mobile**: Flutter (Dart) - Integración nativa para sensores de cámara y GPS.
- **Database**: PostgreSQL/SQLite con SQLAlchemy para integridad referencial.

---

## 🔍 Tabla de Cumplimiento (Checklist Examen)

- [x] Arquitectura Basada en Servicios (Monolito Modular)
- [x] App Móvil de Reportes (Flutter)
- [x] App Web de Gestión (Angular)
- [x] Geolocalización en tiempo real
- [x] Integración IA (Visión y Audio)
- [x] Sistema de Priorización (Severidad IA)
- [x] Asignación Inteligente de Talleres
- [x] Gestión de Notificaciones
- [x] Trazabilidad Completa (Auditoría P6)
- [x] Pagos y Comisión del 10%

---
**Nota para el Evaluador**: Este sistema fue diseñado bajo principios SOLID y Clean Architecture, permitiendo que sea fácilmente portable a una infraestructura de microservicios en el futuro.
