"""
Servicio de email transaccional via Brevo SMTP.

Usa smtplib (stdlib de Python — sin dependencias extra).
Envía HTML responsivo con el mismo diseño neon de la plataforma.
"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════
# PLANTILLAS HTML
# ═══════════════════════════════════════════════════════════════════════

def _base_html(titulo: str, contenido: str) -> str:
    """Plantilla base con diseño neon de RutAIGeoProxi."""
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>{titulo}</title>
</head>
<body style="margin:0;padding:0;background:#0A0E1A;font-family:'Inter',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0A0E1A;padding:40px 20px;">
    <tr>
      <td align="center">
        <table width="580" cellpadding="0" cellspacing="0"
               style="background:#111629;border:1px solid #1F2744;border-radius:16px;overflow:hidden;max-width:580px;">

          <!-- Header -->
          <tr>
            <td style="background:linear-gradient(135deg,#0A0E1A,#111629);padding:32px;text-align:center;border-bottom:1px solid #1F2744;">
              <div style="display:inline-block;width:40px;height:40px;background:#00F2FF;border-radius:50%;line-height:40px;font-weight:bold;color:#000;font-size:18px;">R</div>
              <h1 style="margin:12px 0 0;color:#00F2FF;font-size:18px;letter-spacing:3px;font-family:monospace;">RutAIGeoProxi</h1>
              <p style="margin:4px 0 0;color:#6B7280;font-size:12px;">Sistema de Asistencia Técnica Vehicular con IA</p>
            </td>
          </tr>

          <!-- Contenido -->
          <tr>
            <td style="padding:36px 40px;">
              {contenido}
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="padding:20px 40px;border-top:1px solid #1F2744;text-align:center;">
              <p style="color:#374151;font-size:11px;margin:0;">
                Este correo fue enviado automáticamente por RutAIGeoProxi.<br/>
                Si no solicitaste esto, ignora este mensaje.<br/>
                © 2025 RutAIGeoProxi · Santa Cruz de la Sierra, Bolivia.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def _reset_password_html(nombre: str, reset_link: str, expira_horas: int = 1) -> str:
    """Email para recuperación de contraseña (CU4)."""
    contenido = f"""
      <h2 style="color:#ffffff;font-size:20px;margin:0 0 12px;">Hola, {nombre} 👋</h2>
      <p style="color:#9CA3AF;font-size:14px;line-height:1.6;margin:0 0 24px;">
        Recibimos una solicitud para restablecer la contraseña de tu cuenta.<br/>
        Haz clic en el botón para crear una nueva contraseña. Este enlace es válido por <strong style="color:#00F2FF;">{expira_horas} hora(s)</strong>.
      </p>

      <!-- CTA Button -->
      <div style="text-align:center;margin:32px 0;">
        <a href="{reset_link}"
           style="display:inline-block;background:linear-gradient(135deg,#00F2FF,#0096FF);
                  color:#000;font-weight:bold;text-decoration:none;
                  padding:14px 36px;border-radius:50px;font-size:14px;
                  letter-spacing:1px;">
          🔑 Restablecer Contraseña
        </a>
      </div>

      <!-- Token manual -->
      <div style="background:#0A0E1A;border:1px solid #1F2744;border-radius:8px;padding:16px;margin:24px 0;">
        <p style="color:#6B7280;font-size:11px;margin:0 0 6px;">O copia y pega este enlace en tu navegador:</p>
        <p style="color:#00F2FF;font-size:11px;word-break:break-all;margin:0;">{reset_link}</p>
      </div>

      <p style="color:#4B5563;font-size:12px;margin:0;">
        ⏰ Este enlace expira en <strong>{expira_horas} hora</strong>.<br/>
        Si no solicitaste el cambio, tu contraseña no ha sido modificada.
      </p>
    """
    return _base_html("Restablecer contraseña — RutAIGeoProxi", contenido)


def _welcome_html(nombre: str, login_link: str) -> str:
    """Email de bienvenida al registrarse (CU3)."""
    contenido = f"""
      <h2 style="color:#ffffff;font-size:20px;margin:0 0 12px;">¡Bienvenido, {nombre}! 🎉</h2>
      <p style="color:#9CA3AF;font-size:14px;line-height:1.6;margin:0 0 24px;">
        Tu cuenta en <strong style="color:#00F2FF;">RutAIGeoProxi</strong> fue creada exitosamente.<br/>
        Ya puedes reportar incidentes vehiculares y recibir asistencia técnica en minutos.
      </p>

      <div style="text-align:center;margin:32px 0;">
        <a href="{login_link}"
           style="display:inline-block;background:linear-gradient(135deg,#00F2FF,#0096FF);
                  color:#000;font-weight:bold;text-decoration:none;
                  padding:14px 36px;border-radius:50px;font-size:14px;
                  letter-spacing:1px;">
          🚀 Iniciar Sesión
        </a>
      </div>

      <div style="background:#0A0E1A;border-radius:8px;padding:16px;margin:24px 0;">
        <p style="color:#00F2FF;font-size:13px;font-weight:bold;margin:0 0 8px;">🤖 Lo que puedes hacer:</p>
        <ul style="color:#9CA3AF;font-size:13px;margin:0;padding-left:16px;">
          <li style="margin-bottom:4px;">📍 Reportar incidentes con GPS, fotos y audio</li>
          <li style="margin-bottom:4px;">🤖 Clasificación automática por IA (YOLOv8 + Whisper)</li>
          <li style="margin-bottom:4px;">🏪 Asignación al taller más cercano en segundos</li>
        </ul>
      </div>
    """
    return _base_html("¡Bienvenido a RutAIGeoProxi!", contenido)


def _account_locked_html(nombre: str, motivo: str, soporte_email: str) -> str:
    """Email de cuenta bloqueada permanentemente."""
    contenido = f"""
      <h2 style="color:#FF6B6B;font-size:20px;margin:0 0 12px;">⛔ Cuenta Bloqueada</h2>
      <p style="color:#9CA3AF;font-size:14px;line-height:1.6;margin:0 0 24px;">
        Hola, <strong style="color:#fff;">{nombre}</strong>.<br/>
        Tu cuenta ha sido bloqueada por motivos de seguridad.
      </p>

      <div style="background:#3B0000;border:1px solid rgba(255,107,107,0.3);border-radius:8px;padding:16px;margin:16px 0;">
        <p style="color:#FF6B6B;font-size:13px;margin:0;"><strong>Motivo:</strong> {motivo}</p>
      </div>

      <p style="color:#9CA3AF;font-size:14px;margin:24px 0 0;">
        Para desbloquear tu cuenta, contacta al administrador:<br/>
        <a href="mailto:{soporte_email}" style="color:#00F2FF;">{soporte_email}</a>
      </p>
    """
    return _base_html("Cuenta bloqueada — RutAIGeoProxi", contenido)


# ═══════════════════════════════════════════════════════════════════════
# EMAIL SERVICE
# ═══════════════════════════════════════════════════════════════════════

class EmailService:
    """Servicio de email transaccional via Brevo SMTP."""

    @staticmethod
    def _send(to_email: str, to_name: str, subject: str, html_body: str) -> bool:
        """Envía un email HTML via Brevo SMTP."""
        if not settings.email_enabled:
            logger.warning("[EMAIL] Brevo no configurado — email no enviado a %s", to_email)
            return False

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.BREVO_FROM_NAME} <{settings.BREVO_FROM_EMAIL}>"
        msg["To"] = f"{to_name} <{to_email}>"

        msg.attach(MIMEText(html_body, "html", "utf-8"))

        try:
            with smtplib.SMTP(settings.BREVO_SMTP_HOST, settings.BREVO_SMTP_PORT, timeout=15) as server:
                server.ehlo()
                server.starttls()
                server.login(settings.BREVO_SMTP_LOGIN, settings.BREVO_SMTP_KEY)
                server.sendmail(settings.BREVO_FROM_EMAIL, [to_email], msg.as_string())
            logger.info("[EMAIL] Enviado: %s → %s", subject, to_email)
            return True
        except smtplib.SMTPException as exc:
            logger.error("[EMAIL] Error SMTP enviando a %s: %s", to_email, exc)
            return False

    @classmethod
    def send_reset_password(cls, to_email: str, nombre: str, token: str) -> bool:
        """Envía email de recuperación de contraseña con link al frontend."""
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        html = _reset_password_html(nombre, reset_link)
        return cls._send(
            to_email, nombre,
            "🔑 Recuperar contraseña — RutAIGeoProxi",
            html,
        )

    @classmethod
    def send_welcome(cls, to_email: str, nombre: str) -> bool:
        """Envía email de bienvenida tras el registro."""
        html = _welcome_html(nombre, f"{settings.FRONTEND_URL}/login")
        return cls._send(
            to_email, nombre,
            "🎉 ¡Bienvenido a RutAIGeoProxi!",
            html,
        )

    @classmethod
    def send_account_locked(cls, to_email: str, nombre: str) -> bool:
        """Notifica al usuario que su cuenta fue bloqueada permanentemente."""
        html = _account_locked_html(
            nombre,
            "Límite de intentos de inicio de sesión excedido",
            "soporte@rutaigeoproxi.com",
        )
        return cls._send(
            to_email, nombre,
            "⛔ Tu cuenta fue bloqueada — RutAIGeoProxi",
            html,
        )
