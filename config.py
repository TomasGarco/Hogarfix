import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv


# Carga el .env desde la raíz del proyecto con ruta explícita
_env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=_env_path, override=True)


class Config:
    # SEGURIDAD: nunca usar la clave por defecto en producción
    _raw_secret = os.environ.get("FLASK_SECRET_KEY") or os.environ.get("SECRET_KEY", "")
    if not _raw_secret or _raw_secret == "hogarfix-dev-secret":
        import warnings
        warnings.warn(
            "⚠️  SECRET_KEY no configurada o usa valor por defecto. "
            "Define FLASK_SECRET_KEY en el .env antes de producción.",
            stacklevel=2,
        )
    SECRET_KEY = _raw_secret or "hogarfix-dev-secret"

    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.environ.get("MYSQL_PORT", 3306))
    MYSQL_USER = os.environ.get("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
    MYSQL_DB = os.environ.get("MYSQL_DB", "hogarfix_db")

    _encoded_password = quote_plus(MYSQL_PASSWORD)
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{MYSQL_USER}:{_encoded_password}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
        f"?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = True
    UPLOAD_FOLDER = os.path.join("app", "static", "uploads")
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024

    # Email (SMTP) settings for welcome and notification emails.
    MAIL_ENABLED = os.environ.get("MAIL_ENABLED", "true").lower() == "true"
    MAIL_BACKEND = os.environ.get("MAIL_BACKEND", "smtp")
    MAIL_HOST = os.environ.get("MAIL_HOST", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL", "false").lower() == "true"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")

    # Gmail SMTP fallback (mismos valores por defecto para alta disponibilidad)
    MAIL_SMTP_HOST_FALLBACK = os.environ.get("MAIL_SMTP_HOST_FALLBACK", "smtp.gmail.com")
    MAIL_SMTP_PORT_FALLBACK = int(os.environ.get("MAIL_SMTP_PORT_FALLBACK", 587))
    MAIL_SMTP_USERNAME_FALLBACK = os.environ.get("MAIL_SMTP_USERNAME_FALLBACK", MAIL_USERNAME)
    MAIL_SMTP_PASSWORD_FALLBACK = os.environ.get("MAIL_SMTP_PASSWORD_FALLBACK", MAIL_PASSWORD)
    MAIL_SMTP_USE_TLS_FALLBACK = os.environ.get("MAIL_SMTP_USE_TLS_FALLBACK", "true").lower() == "true"
    MAIL_SMTP_USE_SSL_FALLBACK = os.environ.get("MAIL_SMTP_USE_SSL_FALLBACK", "false").lower() == "true"
    MAIL_FROM = os.environ.get("MAIL_FROM", MAIL_USERNAME or "no-reply@hogarfix.co")
    MAIL_TIMEOUT = int(os.environ.get("MAIL_TIMEOUT", 8))

    # Wompi (pasarela de pagos colombiana)
    WOMPI_PUBLIC_KEY   = os.environ.get("WOMPI_PUBLIC_KEY", "")
    WOMPI_PRIVATE_KEY  = os.environ.get("WOMPI_PRIVATE_KEY", "")
    WOMPI_EVENTS_SECRET = os.environ.get("WOMPI_EVENTS_SECRET", "")
    WOMPI_INTEGRITY_SECRET = os.environ.get("WOMPI_INTEGRITY_SECRET", "")
    WOMPI_SANDBOX      = os.environ.get("WOMPI_SANDBOX", "true").lower() == "true"
    MAIL_FILE_PATH = os.environ.get("MAIL_FILE_PATH", os.path.join("app", "mail_outbox.log"))
    MAIL_API_TOKEN = os.environ.get("MAIL_API_TOKEN", "")
    MAIL_API_URL = os.environ.get("MAIL_API_URL", "https://api.mailersend.com/v1/email")
    MAIL_FROM_NAME = os.environ.get("MAIL_FROM_NAME", "HogarFix")
    MAIL_LOGO_URL = os.environ.get("MAIL_LOGO_URL", "")
    MAIL_PUBLIC_BASE_URL = os.environ.get("MAIL_PUBLIC_BASE_URL", "")
    MAIL_FACEBOOK_URL = os.environ.get("MAIL_FACEBOOK_URL", "")
    MAIL_INSTAGRAM_URL = os.environ.get("MAIL_INSTAGRAM_URL", "")
    MAIL_LINKEDIN_URL = os.environ.get("MAIL_LINKEDIN_URL", "")
    MAIL_YOUTUBE_URL = os.environ.get("MAIL_YOUTUBE_URL", "")
    ADMIN_LOGIN_CODE = os.environ.get("ADMIN_LOGIN_CODE", "")
    ADMIN_REGISTER_CODE = os.environ.get("ADMIN_REGISTER_CODE", "")
    ADMIN_SECURITY_MAX_ATTEMPTS = int(os.environ.get("ADMIN_SECURITY_MAX_ATTEMPTS", 3))
    ADMIN_SECURITY_BLOCK_MINUTES = int(os.environ.get("ADMIN_SECURITY_BLOCK_MINUTES", 15))
    GOOGLE_MAPS_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "")

    GOOGLE_OAUTH_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "")
    GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", "")
    GOOGLE_OAUTH_REDIRECT_URI = os.environ.get("GOOGLE_OAUTH_REDIRECT_URI", "")
    MICROSOFT_OAUTH_CLIENT_ID = os.environ.get("MICROSOFT_OAUTH_CLIENT_ID", "")
    MICROSOFT_OAUTH_CLIENT_SECRET = os.environ.get("MICROSOFT_OAUTH_CLIENT_SECRET", "")
    MICROSOFT_OAUTH_TENANT_ID = os.environ.get("MICROSOFT_OAUTH_TENANT_ID", "common")
    MICROSOFT_OAUTH_REDIRECT_URI = os.environ.get("MICROSOFT_OAUTH_REDIRECT_URI", "")
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "false").lower() == "true"
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE
    PREFERRED_URL_SCHEME = os.environ.get("PREFERRED_URL_SCHEME", "http")

    OTP_TTL_MINUTES = 2
    OTP_MAX_ATTEMPTS = int(os.environ.get("OTP_MAX_ATTEMPTS", 3))
    OTP_RESEND_SECONDS = int(os.environ.get("OTP_RESEND_SECONDS", 60))

    # Identity verification providers (Onfido / Veriff)
    IDENTITY_PROVIDER = os.environ.get("IDENTITY_PROVIDER", "mock")
    ONFIDO_API_KEY = os.environ.get("ONFIDO_API_KEY", "")
    ONFIDO_VERIFY_ENDPOINT = os.environ.get("ONFIDO_VERIFY_ENDPOINT", "")
    ONFIDO_WEBHOOK_TOKEN = os.environ.get("ONFIDO_WEBHOOK_TOKEN", "")
    VERIFF_API_KEY = os.environ.get("VERIFF_API_KEY", "")
    VERIFF_VERIFY_ENDPOINT = os.environ.get("VERIFF_VERIFY_ENDPOINT", "")
    VERIFF_WEBHOOK_TOKEN = os.environ.get("VERIFF_WEBHOOK_TOKEN", "")
