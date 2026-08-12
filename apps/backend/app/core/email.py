import smtplib
from email.message import EmailMessage
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

def send_email(to_email: str, subject: str, html_content: str):
    if not settings.SMTP_HOST:
        logger.warning(f"SMTP_HOST not configured. Would have sent email to {to_email}: {subject}")
        return

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = settings.MAIL_FROM
    msg['To'] = to_email
    msg.add_alternative(html_content, subtype='html')

    try:
        if settings.SMTP_PORT == 465:
            # SSL
            with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                if settings.SMTP_USER and settings.SMTP_PASSWORD:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        else:
            # TLS or unencrypted
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                if settings.SMTP_USER and settings.SMTP_PASSWORD:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        logger.info(f"Successfully sent email to {to_email}: {subject}")
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")

def send_welcome_email(to_email: str):
    subject = "Welcome to Snaply!"
    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #070B0F; color: #EEF7FA; padding: 40px; text-align: center;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #0E141B; padding: 40px; border-radius: 12px; border: 1px solid rgba(217, 235, 242, 0.09);">
          <h1 style="color: #24C8DB;">Welcome to Snaply 🚀</h1>
          <p style="font-size: 16px; line-height: 1.5; color: #9CAAB2;">
            Hi there!<br><br>
            Thank you for joining Snaply. You can now easily capture and share your screen in seconds.<br>
            Use <strong>Ctrl+Shift+S</strong> on the desktop app to get started.
          </p>
          <a href="https://snaply-dev.github.io" style="display: inline-block; margin-top: 20px; padding: 12px 24px; background-color: #24C8DB; color: #ffffff; text-decoration: none; border-radius: 6px; font-weight: bold;">
            Visit Website
          </a>
        </div>
      </body>
    </html>
    """
    send_email(to_email, subject, html_content)
