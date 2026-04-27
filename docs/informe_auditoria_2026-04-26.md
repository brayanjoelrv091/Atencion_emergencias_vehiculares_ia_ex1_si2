# Informe de Auditoria Tecnica - 2026-04-26

## 1. Resumen ejecutivo

Se revisaron las carpetas `backend`, `frontend`, `mobile`, `landing` y `docs`.

Estado general despues de la correccion:

- Backend FastAPI: compila, levanta e implementa los modulos P1-P6.
- Frontend Angular: compila correctamente con `npm run build`.
- Mobile Flutter: queda sin issues en `flutter analyze` y con `flutter test` pasando.
- Smoke test funcional en BD temporal: login, registro, recuperacion, vehiculos, incidentes, clasificacion, asignacion, flujo de taller, pagos, tracking WS y reportes PDF/Excel respondieron OK.

## 2. Problemas corregidos en esta auditoria

1. Mobile tinha referencias rotas entre `screens/` viejas y `modules/` nuevos.
2. Mobile usaba endpoints incorrectos para recuperacion de contrasena.
3. Mobile tinha placeholders rotos para reporte y detalle de incidente.
4. Mobile tinha configuracion inconsistente para URL base y WebSocket.
5. Backend de pagos notificaba por `incident_id` en lugar de `user_id`, por lo que CU16/CU17 fallaban en silencio.
6. Backend de pagos no validaba correctamente autorizacion ni duplicidad de pago.
7. Reportes PDF/Excel estaban declarados pero en la practica no corrían por dependencias rotas en el entorno local.
8. Pantalla web de pagos dependia de un `incidente_id` fijo.
9. Web/mobile mostraban auto-asignacion donde el actor correcto es admin; se dejo acotado para no inducir errores al usuario final.

## 3. Validaciones ejecutadas

### Builds y analisis

- `backend`: `python -m compileall app`
- `frontend`: `npm run build`
- `mobile`: `flutter analyze`
- `mobile`: `flutter test`

### Smoke test API en BD temporal

Se verifico en una base temporal aislada:

- `CU01` login admin/cliente/taller
- `CU03` registro cliente/taller
- `CU04` forgot/reset password
- `CU05` listado de usuarios y cambio de permisos
- `CU06` alta de vehiculo
- `CU07` alta de incidente
- `CU08` reclasificacion
- `CU09` detalle de incidente
- `CU10` alta de taller y tecnico
- `CU11` recepcion de solicitudes
- `CU12` cambio de estado `pendiente -> proceso -> atendido`
- `CU13` historial de atenciones
- `CU14` auto-asignacion
- `CU15` websocket de tracking
- `CU16/CU17` websocket de notificacion de pago
- `CU18` pago
- `CU19/CU20` exportacion PDF/Excel e historial de reportes

Resultado del smoke test principal:

- Todos los endpoints anteriores respondieron `200/201/204` despues de la correccion.
- La clasificacion quedo operativa por reglas; `YOLOv8` y `Whisper` no estaban instalados en el entorno verificado.

## 4. Credenciales y secretos encontrados

### Credenciales demo funcionales

Detectadas en BD/seed:

- `admin@ruta.com / Password123`
- `taller@ruta.com / Password123`
- `cliente@ruta.com / Password123`

Detectadas en `backend/.env`:

- `admin@rutaigeoproxi.com / Admin2026!#`

Archivos relacionados:

- `backend/seed_demo_users_fixed.py`
- `backend/.env`
- `README.md`

### Riesgo de seguridad actual

En `backend/.env` hay secretos reales/versionados:

- `SECRET_KEY`
- `SMTP_USER`
- `SMTP_PASSWORD`

Observacion: estos secretos deben rotarse y salir del repo. No reproduzco aqui el valor completo del SMTP porque ya esta disponible en el archivo local y es sensible.

## 5. Conexiones entre capas

### Backend

- API principal: `backend/app/main.py`
- DB local actual: `backend/.env` -> `sqlite:///./rutaigeoproxi.db`
- Storage: local en `backend/uploads`
- Storage alternativo: Firebase opcional via `backend/app/shared/storage.py`
- Email: SMTP Brevo via `backend/app/shared/email.py`

### Frontend web -> backend

- Base URL: `frontend/src/app/environment.ts` -> `http://127.0.0.1:8000`
- WebSocket notificaciones: `frontend/src/app/modules/shared/websocket.service.ts`
- WebSocket tracking: `frontend/src/app/modules/shared/websocket.service.ts`

### Mobile -> backend

- Base URL Android emulator: `http://10.0.2.2:8000`
- Base URL desktop/iOS/web local: `http://127.0.0.1:8000`
- Archivo: `mobile/lib/config.dart`
- Cliente HTTP: `mobile/lib/core/api_client.dart`
- Tracking WS: `mobile/lib/core/location_service.dart`

## 6. Estado por caso de uso

| CU | Backend | Frontend web | Mobile | Estado actual | Comentario |
|---|---|---|---|---|---|
| CU-01 Gestionar Inicio de Sesion | `backend/app/modules/p1_usuarios/routes.py`, `services.py` | `frontend/src/app/modules/p1_usuarios/auth.service.ts`, `pages/login/*` | `mobile/lib/modules/auth/services/auth_service.dart`, `screens/login_screen.dart` | Cumple | Verificado por smoke test. |
| CU-02 Gestionar Cierre de Sesion | `backend/app/modules/p1_usuarios/routes.py`, `services.py` | `frontend/src/app/modules/p1_usuarios/auth.service.ts` | `mobile/lib/modules/auth/services/auth_service.dart`, `mobile/lib/main.dart` | Cumple | Se corrigio logout mobile para pegar al backend. |
| CU-03 Registrar Usuario | `backend/app/modules/p1_usuarios/routes.py`, `schemas.py`, `services.py` | `frontend/src/app/modules/p1_usuarios/auth.service.ts`, `pages/register/*` | `mobile/lib/modules/auth/services/auth_service.dart`, `screens/register_screen.dart` | Cumple | Verificado por smoke test. |
| CU-04 Recuperar Contrasena | `backend/app/modules/p1_usuarios/routes.py`, `services.py` | `frontend/src/app/modules/p1_usuarios/pages/forgot-password/*`, `reset-password/*` | `mobile/lib/modules/auth/screens/forgot_password_screen.dart`, `mobile/lib/screens/reset_password_screen.dart` | Cumple | Verificado por smoke test. En pruebas se uso `DEBUG_RESET_TOKEN=true`. |
| CU-05 Gestionar roles y permisos | `backend/app/modules/p1_usuarios/routes.py` (`/admin/users*`) | `frontend/src/app/modules/p1_usuarios/pages/admin-users/*` | Sin UI activa | Parcial | Backend y web admin OK; mobile no lo expone. |
| CU-06 Gestionar datos del usuario y vehiculo | `backend/app/modules/p1_usuarios/routes.py` (`/me`, `/me/vehicles`) | `frontend/src/app/modules/p1_usuarios/pages/home/*` | Codigo legacy en `mobile/lib/screens/home_screen.dart`, no integrado en la app actual | Parcial | Backend y web OK; mobile actual no lo tiene en navegacion principal. |
| CU-07 Reportar incidente con ubicacion, fotos y audio | `backend/app/modules/p2_incidentes/routes.py`, `services.py` | `frontend/src/app/modules/p2_incidentes/pages/incidents/report-incident/*` | `mobile/lib/screens/report_incident_screen.dart` | Parcial | Backend/web soportan multipart; mobile actual reporta texto+GPS pero no captura fotos/audio reales. |
| CU-08 Clasificacion automatica del incidente (IA) | `backend/app/modules/p2_incidentes/classifier.py`, `services.py` | Servicio en `frontend/src/app/modules/p2_incidentes/incident.service.ts` | Sin UI dedicada | Parcial | Opera por reglas; YOLO/Whisper no verificados en este entorno. |
| CU-09 Generar ficha estructurada del incidente | `backend/app/modules/p2_incidentes/routes.py` (`GET /incidents/{id}`) | `frontend/src/app/modules/p2_incidentes/pages/incidents/incident-detail/*` | `mobile/lib/modules/incidents/screens/incident_detail_screen.dart` | Cumple | Verificado por smoke test. |
| CU-10 Registrar taller y tecnicos disponibles | `backend/app/modules/p3_talleres/routes.py`, `services.py` | `frontend/src/app/modules/p3_talleres/pages/workshops/register-workshop/*` | Sin UI activa | Parcial | Backend/web OK; mobile no implementa ese flujo. |
| CU-11 Recepcion de solicitudes de asistencia | `backend/app/modules/p3_talleres/routes.py` (`/workshops/{id}/requests`) | `frontend/src/app/modules/p3_talleres/pages/workshops/service-requests/*` | Sin UI activa | Parcial | Backend/web OK; mobile no implementa ese flujo. |
| CU-12 Actualizacion del estado del servicio | `backend/app/modules/p3_talleres/routes.py` (`/requests/{id}/status`) | `frontend/src/app/modules/p3_talleres/pages/workshops/service-requests/*` | Sin UI activa | Parcial | Verificado por smoke test en backend; mobile no implementa ese flujo. |
| CU-13 Visualizacion de historial de atenciones | `backend/app/modules/p3_talleres/routes.py` (`/workshops/{id}/history`) | `frontend/src/app/modules/p3_talleres/pages/workshops/service-history/*` | Sin UI activa | Parcial | Backend/web OK; mobile no implementa ese flujo. |
| CU-14 Asignacion automatica del taller mas adecuado | `backend/app/modules/p4_asignacion/routes.py`, `services.py` | `frontend/src/app/modules/p4_asignacion/assignment.service.ts`, `my-incidents/*` | Servicio en `mobile/lib/modules/assignments/assignment_service.dart` | Parcial | Backend y web admin OK; mobile no expone flujo admin. |
| CU-15 Geolocalizacion avanzada del servicio | `backend/app/modules/p4_asignacion/routes.py` (WS tracking) | `frontend/src/app/modules/p4_asignacion/pages/geo-tracking/*`, `shared/websocket.service.ts` | `mobile/lib/core/location_service.dart` | Parcial | Web verificado a nivel de codigo; backend WS verificado por smoke test; mobile aun sin pantalla integrada. |
| CU-16 Notificaciones push al cliente y taller | `backend/app/modules/p5_pagos/routes.py`, `services.py`, `shared/websocket_manager.py` | Solo servicio WS en `frontend/src/app/modules/shared/websocket.service.ts` | Sin UI de notificaciones | Parcial | Se corrigio el bug de canal de notificacion. Backend verificado por smoke test. |
| CU-17 Actualizaciones en tiempo real del estado del servicio | Backend WS en pagos/asignacion | `frontend/src/app/modules/shared/websocket.service.ts`, `p4_asignacion/pages/geo-tracking/*` | `mobile/lib/core/location_service.dart` | Parcial | Existe infraestructura; falta una experiencia completa de estado en mobile y una UI de notificaciones en web. |
| CU-18 Procesamiento de pagos en linea | `backend/app/modules/p5_pagos/routes.py`, `services.py` | `frontend/src/app/modules/p5_pagos/pages/payments/*` | `mobile/lib/screens/payment_screen.dart` (no integrado en rutas principales) | Parcial | Backend/web OK y backend verificado; mobile tiene pantalla pero no flujo completo desde navegacion principal. |
| CU-19 Generar reporte de incidentes atendidos | `backend/app/modules/p6_reportes/services.py`, `routes.py` | `frontend/src/app/modules/p6_reportes/pages/reportes/*` | Sin UI activa | Parcial | Backend/web OK tras reparar dependencias del entorno. |
| CU-20 Exportar reportes en PDF y Excel | `backend/app/modules/p6_reportes/routes.py`, `services.py` | `frontend/src/app/modules/p6_reportes/pages/reportes/*` | Sin UI activa | Parcial | Verificado por smoke test con `200` para PDF y Excel. |

## 7. Estado real de cumplimiento

### Casos de uso que ya cumplen bien en backend + web y/o mobile

- CU-01
- CU-02
- CU-03
- CU-04
- CU-09

### Casos de uso que cumplen a nivel backend pero no estan completos en las 3 capas

- CU-05
- CU-06
- CU-07
- CU-08
- CU-10
- CU-11
- CU-12
- CU-13
- CU-14
- CU-15
- CU-16
- CU-17
- CU-18
- CU-19
- CU-20

## 8. Riesgos y observaciones importantes

1. `backend/.env` tiene secretos reales y debe tratarse como material sensible.
2. La clasificacion IA funciona hoy por reglas; no se validaron modelos pesados (`ultralytics`, `openai-whisper`).
3. Mobile sigue mas maduro para autenticacion e incidentes que para administracion, talleres, pagos y reportes.
4. Web es hoy la capa mas completa para operacion administrativa.
5. El sistema usa SQLite local por defecto; para carga real multiusuario convendria migrar a PostgreSQL.

## 9. Recomendacion de prioridad

### Alta

1. Sacar secretos del repo y rotarlos.
2. Completar UI mobile para CU06, CU10-CU18.
3. Exponer correctamente CU08/CU16/CU17 en pantallas web/mobile, no solo en servicios.

### Media

1. Agregar pruebas automaticas permanentes para backend.
2. Agregar pruebas de integracion para frontend.
3. Crear seeds consistentes para demo integral de tribunal.

## 10. Archivos clave auditados

- `backend/app/main.py`
- `backend/app/modules/p1_usuarios/*`
- `backend/app/modules/p2_incidentes/*`
- `backend/app/modules/p3_talleres/*`
- `backend/app/modules/p4_asignacion/*`
- `backend/app/modules/p5_pagos/*`
- `backend/app/modules/p6_reportes/*`
- `backend/app/shared/*`
- `frontend/src/app/app.routes.ts`
- `frontend/src/app/modules/**/*`
- `mobile/lib/main.dart`
- `mobile/lib/core/*`
- `mobile/lib/modules/**/*`
- `mobile/lib/screens/*`