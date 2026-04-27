import smtplib
from email.message import EmailMessage
from app.shared.config import settings

def send_reset_email(to_email: str, token: str):
    """
    Envía el correo de recuperación de contraseña vía Brevo (SMTP).
    """
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        print("SMTP no configurado. No se enviará correo.")
        return

    # Usamos la URL local para el desarrollo (Angular)
    reset_url = f"http://localhost:4200/reset-password?token={token}"

    msg = EmailMessage()
    msg['Subject'] = "Recuperación de Contraseña - RutAIGeoProxi"
    msg['From'] = settings.FROM_EMAIL
    msg['To'] = to_email

    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #0096FF;">Recupera tu acceso a RutAIGeoProxi</h2>
        <p>Hola,</p>
        <p>Hemos recibido una solicitud para restablecer tu contraseña. Haz clic en el botón de abajo para crear una nueva contraseña:</p>
        <div style="text-align: center; margin: 30px 0;">
          <a href="{reset_url}" style="background-color: #00F2FF; color: #000; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
            Restablecer Contraseña
          </a>
        </div>
        <p>O copia y pega el siguiente enlace en tu navegador:</p>
        <p style="word-break: break-all; font-size: 14px; color: #555;">{reset_url}</p>
        <p>Si no fuiste tú quien solicitó el cambio, ignora este correo. El enlace expira en 1 hora.</p>
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;" />
        <p style="font-size: 12px; color: #999; text-align: center;">El equipo de RutAIGeoProxi</p>
      </body>
    </html>
    """
    msg.set_content(html_content, subtype='html')

    try:
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
