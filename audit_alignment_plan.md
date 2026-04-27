# Auditoría de Alineación de Roles — RutAIGeoProxi

Este documento detalla la lógica de roles (Admin, Taller, Cliente) y los hallazgos de la auditoría de seguridad e integración realizada.

## 👥 Definición de Roles y Funciones

| Rol | Descripción | Funciones Principales |
| :--- | :--- | :--- |
| **Admin** | Superusuario del sistema. | Gestión de usuarios, talleres, reporte global, auditoría total. |
| **Taller** | Entidad de servicio técnico. | Gestión de técnicos, recepción de solicitudes, actualización de estados. |
| **Cliente** | Usuario final (dueño de coche). | Registro de vehículos, reporte de incidentes, seguimiento y pagos. |

## 🔍 Hallazgos de la Auditoría

He revisado "cada carpeta y archivo" y he encontrado las siguientes inconsistencias en la **fusión** de los módulos:

1. **Brecha en P6 Reportes**: Los endpoints `/reports/incidents/pdf` y `excel` no verifican el rol 'admin', permitiendo acceso a cualquier usuario autenticado.
2. **Brecha en P5 Pagos**: El `/history` de pagos devuelve todos los registros de la BD sin filtrar por el dueño, lo cual es un error de privacidad.
3. **Falta de Guards en Frontend**: El archivo `app.routes.ts` importa `roleGuard` pero no lo aplica a las rutas de `/admin-users` ni `/reports`.
4. **Residuos de Demo**: Algunas rutas en el backend tienen comentarios de "facilitar la demo" que deshabilitan la seguridad real.

## 🛠 Lógica de Alineación Propuesta

Para que todo se vea reflejado según el rol (tu solicitud), implementaremos:

- **Backend**:
  - Restricción estricta de rutas administrativas (`require_roles("admin")`).
  - Filtrado de datos en servicios según el `user_id` y `rol` del solicitante.
- **Frontend**:
  - Protección de rutas en Angular mediante `canActivate`.
  - Hiding/Showing dinámico de componentes en el Navbar basado en `user_role`.

---
*Este plan será ejecutado tras tu aprobación.*
