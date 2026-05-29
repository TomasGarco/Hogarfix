from datetime import datetime
import logging

from flask import Flask, redirect, render_template, request, session, url_for
import click
from flask_login import current_user, logout_user
from sqlalchemy import or_
from sqlalchemy.exc import OperationalError, SQLAlchemyError

from flask import jsonify
from app.extensions import csrf, db, limiter, login_manager, oauth, oauth_available, socketio
from app.models import Announcement, Notification, User, UserSession
from app.utils import send_email
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Logging estructurado a archivo (no expone errores al usuario)
    if not app.debug:
        import os
        log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
        os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.FileHandler(os.path.join(log_dir, "hogarfix.log"), encoding="utf-8")
        file_handler.setLevel(logging.WARNING)
        file_handler.setFormatter(logging.Formatter(
            "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
        ))
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.WARNING)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    socketio.init_app(app, async_mode='threading', cors_allowed_origins='*')
    if oauth_available:
        oauth.init_app(app)

        if app.config.get("GOOGLE_OAUTH_CLIENT_ID") and app.config.get("GOOGLE_OAUTH_CLIENT_SECRET"):
            oauth.register(
                name="google",
                client_id=app.config.get("GOOGLE_OAUTH_CLIENT_ID"),
                client_secret=app.config.get("GOOGLE_OAUTH_CLIENT_SECRET"),
                server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
                client_kwargs={"scope": "openid email profile"},
            )

        if app.config.get("MICROSOFT_OAUTH_CLIENT_ID") and app.config.get("MICROSOFT_OAUTH_CLIENT_SECRET"):
            tenant_id = app.config.get("MICROSOFT_OAUTH_TENANT_ID", "common")
            oauth.register(
                name="microsoft",
                client_id=app.config.get("MICROSOFT_OAUTH_CLIENT_ID"),
                client_secret=app.config.get("MICROSOFT_OAUTH_CLIENT_SECRET"),
                server_metadata_url=(
                    f"https://login.microsoftonline.com/{tenant_id}/v2.0/.well-known/openid-configuration"
                ),
                client_kwargs={"scope": "openid email profile User.Read"},
            )

    app.config["SOCIAL_AUTH_AVAILABLE"] = oauth_available

    from app.blueprints.admin import admin_bp
    from app.blueprints.api import api_bp
    from app.blueprints.auth import auth_bp
    from app.blueprints.booking import booking_bp
    from app.blueprints.chat import register_socketio_events
    from app.blueprints.main import main_bp
    from app.blueprints.technician import technician_bp

    register_socketio_events(socketio)

    app.register_blueprint(api_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(technician_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(admin_bp)

    # ── Filtros Jinja personalizados ──
    @app.template_filter('format_cop')
    def format_cop(value):
        """Formatea un numero como peso colombiano: $10.000"""
        try:
            n = int(float(str(value).replace('.', '').replace(',', '.').strip()))
            return '${:,.0f}'.format(n).replace(',', '.')
        except (ValueError, TypeError):
            return str(value) if value else ''

    @app.context_processor
    def inject_globals():
        """Inyecta variables globales en todos los templates."""
        count = 0
        _name = ''
        _ini = 'U'
        _photo = ''
        if current_user.is_authenticated:
            try:
                count = Notification.query.filter_by(
                    user_id=current_user.id, is_read=False
                ).count()
            except Exception:
                count = 0
            _name = current_user.full_name or current_user.email.split('@')[0]
            parts = _name.split()
            _ini = ((parts[0][0] if parts else 'U') + (parts[1][0] if len(parts) > 1 else '')).upper()
            _photo = current_user.avatar_url or ''

        # Anuncio activo (el más reciente dentro de fechas válidas)
        active_announcement = None
        try:
            now = datetime.utcnow()
            active_announcement = (
                Announcement.query
                .filter(
                    Announcement.activo == True,
                    or_(Announcement.fecha_inicio.is_(None), Announcement.fecha_inicio <= now),
                    or_(Announcement.fecha_fin.is_(None), Announcement.fecha_fin >= now),
                )
                .order_by(Announcement.created_at.desc())
                .first()
            )
        except Exception as e:
            app.logger.warning("Announcement query failed: %s", e)
            active_announcement = None

        return {
            "g_unread_notif": count,
            "_name": _name,
            "_ini": _ini,
            "_photo": _photo,
            "active_announcement": active_announcement,
        }

    # Excluir Socket.IO del CSRF (usa su propio protocolo)
    csrf.exempt(api_bp)

    @app.after_request
    def set_security_headers(response):
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(self), microphone=(), camera=()"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://unpkg.com https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com https://fonts.googleapis.com; "
            "font-src 'self' https://cdn.jsdelivr.net https://fonts.gstatic.com; "
            "img-src 'self' data: blob: https:; "
            "connect-src 'self' ws: wss: https://nominatim.openstreetmap.org; "
        )
        return response

    @app.errorhandler(429)
    def ratelimit_handler(e):
        if request.accept_mimetypes.best == "application/json":
            return jsonify(error="Demasiadas solicitudes. Intenta más tarde."), 429
        from flask import flash, redirect, url_for
        flash("Demasiados intentos. Espera un momento antes de continuar.", "danger")
        return redirect(request.referrer or url_for("auth.login")), 429

    @app.errorhandler(403)
    def forbidden(e):
        if request.accept_mimetypes.best == "application/json":
            return jsonify(error="Acceso denegado."), 403
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(e):
        if request.accept_mimetypes.best == "application/json":
            return jsonify(error="Recurso no encontrado."), 404
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        app.logger.error(f"Error 500: {e}", exc_info=True)
        if request.accept_mimetypes.best == "application/json":
            return jsonify(error="Error interno del servidor."), 500
        return render_template("errors/500.html"), 500

    @app.errorhandler(OperationalError)
    def db_operational_error(e):
        db.session.rollback()
        app.logger.error(f"DB OperationalError: {e}", exc_info=True)
        if request.accept_mimetypes.best == "application/json":
            return jsonify(error="Base de datos no disponible."), 503
        return render_template("errors/503.html"), 503

    @app.errorhandler(SQLAlchemyError)
    def db_generic_error(e):
        db.session.rollback()
        app.logger.error(f"SQLAlchemyError: {e}", exc_info=True)
        if request.accept_mimetypes.best == "application/json":
            return jsonify(error="Error de base de datos."), 500
        return render_template("errors/500.html"), 500

    @app.before_request
    def protect_private_uploads():
        """Bloquea acceso directo a documentos de verificación — solo admin."""
        if not request.path.startswith("/static/uploads/verification/"):
            return None
        if not current_user.is_authenticated:
            from flask import abort
            abort(403)
        if current_user.role != "admin":
            from flask import abort
            abort(403)
        return None

    @app.before_request
    def enforce_two_factor_state():
        active_session_token = session.get("active_session_token")
        if active_session_token:
            active_session = UserSession.query.filter_by(session_token=active_session_token).first()
            if active_session and active_session.revoked_at is None:
                active_session.last_seen_at = datetime.utcnow()
                db.session.commit()
            elif active_session and active_session.revoked_at is not None:
                logout_user()
                session.pop("user_id", None)
                session.pop("2fa_ok", None)
                session.pop("pre_2fa_user_id", None)
                session.pop("pre_2fa_login_as", None)
                session.pop("active_session_token", None)
                return redirect(url_for("auth.login"))

        if not current_user.is_authenticated:
            return None

        if session.get("2fa_ok"):
            return None

        endpoint = (request.endpoint or "")
        allowed = {
            "auth.logout",
            "auth.login",
            "auth.verify_otp",
            "auth.resend_otp",
        }
        if endpoint.startswith("static") or endpoint in allowed:
            return None

        logout_user()
        session.pop("user_id", None)
        session.pop("2fa_ok", None)
        session.pop("pre_2fa_user_id", None)
        session.pop("pre_2fa_login_as", None)
        session.pop("active_session_token", None)
        return redirect(url_for("auth.login"))

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.context_processor
    def inject_globals():
        unread_notification_count = 0
        recent_notifications = []
        if current_user.is_authenticated and hasattr(current_user, "notifications"):
            unread_notification_count = (
                Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
            )
            recent_notifications = (
                Notification.query.filter_by(user_id=current_user.id)
                .order_by(Notification.created_at.desc())
                .limit(5)
                .all()
            )
        return {
            "tech_types": ["independiente", "empresa_local", "ex_estado"],
            "services_catalog": [
                "plomero",
                "electricista",
                "pintor",
                "cerrajero",
                "fumigador",
                "carpintero",
            ],
            "unread_notification_count": unread_notification_count,
            "recent_notifications": recent_notifications,
        }

    @app.cli.command("mail-test")
    @click.option("--to", required=True, help="Correo destino para la prueba SMTP.")
    def mail_test(to):
        ok, status = send_email(
            subject="Prueba SMTP HogarFix",
            to_email=to,
            text_body="Este es un correo de prueba enviado desde HogarFix.",
            html_body="<p>Este es un correo de <strong>prueba</strong> enviado desde HogarFix.</p>",
        )

        if ok:
            click.echo("Correo de prueba enviado correctamente.")
            return

        click.echo(f"No se pudo enviar el correo. Estado: {status}")
        raise SystemExit(1)

    @app.cli.command("init-db")
    def init_db():
        db.create_all()
        click.echo("Base de datos inicializada.")

    return app
