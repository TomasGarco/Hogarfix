import os
import smtplib
import uuid
import json
import base64
from functools import wraps
from datetime import datetime
from email.message import EmailMessage
from urllib import error as urlerror
from urllib import request as urlrequest
from urllib.parse import urljoin

from flask import abort, current_app, flash, has_request_context, redirect, request, url_for
from flask_login import current_user
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
MAIL_LOGO_CID = "hogarfix-logo"


def _mail_local_logo_asset():
    candidates = (
        ("logo-hogarfix.png", "image/png"),
        ("mascota-fixi.png", "image/png"),
    )
    for filename, mime_type in candidates:
        asset_path = os.path.join(current_app.root_path, "static", "img", filename)
        if os.path.exists(asset_path):
            return asset_path, filename, mime_type
    return "", "", ""


def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if current_user.role not in roles:
                flash("No puedes ingresar al apartado de admin con esta cuenta.", "warning")
                return redirect(url_for("main.dashboard"))
            return f(*args, **kwargs)

        return decorated

    return decorator


def save_upload(file_storage, subfolder):
    if not file_storage or not file_storage.filename:
        return ""

    filename = secure_filename(file_storage.filename)
    extension = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if extension not in ALLOWED_EXTENSIONS:
        return ""

    generated = f"{uuid.uuid4().hex}.{extension}"
    upload_dir = os.path.join(current_app.root_path, "static", "uploads", subfolder)
    os.makedirs(upload_dir, exist_ok=True)
    file_storage.save(os.path.join(upload_dir, generated))
    return f"uploads/{subfolder}/{generated}"


def create_notification(user_id, notif_type, title, message, link_url=None, commit=True):
    from app.extensions import db
    from app.models import Notification

    notification = Notification(
        user_id=user_id,
        type=(notif_type or "general").strip().lower() or "general",
        title=(title or "Actualizacion").strip()[:120],
        message=(message or "").strip(),
        link_url=(link_url or "").strip() or None,
    )
    db.session.add(notification)
    if commit:
        db.session.commit()
        # Push en tiempo real via Socket.IO
        try:
            from app.extensions import socketio
            unread = Notification.query.filter_by(user_id=user_id, is_read=False).count()
            socketio.emit("new_notification", {"count": unread}, to=f"user_{user_id}")
        except Exception:
            pass
    return notification


def send_email(subject, to_email, text_body, html_body=None):
    if not current_app.config.get("MAIL_ENABLED", False):
        return False, "mail-disabled"

    backend = str(current_app.config.get("MAIL_BACKEND", "smtp")).strip().lower()
    host = current_app.config.get("MAIL_HOST", "")
    port = current_app.config.get("MAIL_PORT", 587)
    username = current_app.config.get("MAIL_USERNAME", "")
    password = current_app.config.get("MAIL_PASSWORD", "")
    from_email = current_app.config.get("MAIL_FROM", "no-reply@hogarfix.co")
    use_tls = current_app.config.get("MAIL_USE_TLS", True)
    use_ssl = current_app.config.get("MAIL_USE_SSL", False)
    timeout_secs = int(current_app.config.get("MAIL_TIMEOUT", 8))

    def _send_via_smtp():
        # Usa credenciales de fallback de Gmail si están disponibles
        smtp_host = host or current_app.config.get("MAIL_SMTP_HOST_FALLBACK", "")
        smtp_port = port or current_app.config.get("MAIL_SMTP_PORT_FALLBACK", 587)
        smtp_username = username or current_app.config.get("MAIL_SMTP_USERNAME_FALLBACK", "")
        smtp_password = password or current_app.config.get("MAIL_SMTP_PASSWORD_FALLBACK", "")
        smtp_use_tls = use_tls if use_tls is not None else current_app.config.get("MAIL_SMTP_USE_TLS_FALLBACK", True)
        smtp_use_ssl = use_ssl if use_ssl is not None else current_app.config.get("MAIL_SMTP_USE_SSL_FALLBACK", False)
        
        if not smtp_host or not smtp_username or not smtp_password:
            return False, "mail-missing-config"

        from email.header import Header
        from email.utils import formataddr
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText
        from email.mime.image import MIMEImage

        if html_body:
            # Estructura correcta para imágenes inline CID:
            # related
            #   └── alternative
            #         ├── text/plain
            #         └── text/html
            #   └── image (inline, cid:...)
            has_inline_logo = f"cid:{MAIL_LOGO_CID}" in html_body
            logo_path, logo_name, _ = _mail_local_logo_asset() if has_inline_logo else ("", "", "")

            if has_inline_logo and logo_path:
                msg = MIMEMultipart("related")
                alt = MIMEMultipart("alternative")
                alt.attach(MIMEText(text_body, "plain", "utf-8"))
                alt.attach(MIMEText(html_body, "html", "utf-8"))
                msg.attach(alt)
                with open(logo_path, "rb") as img_f:
                    img = MIMEImage(img_f.read())
                img.add_header("Content-ID", f"<{MAIL_LOGO_CID}>")
                img.add_header("Content-Disposition", "inline", filename=logo_name)
                msg.attach(img)
            else:
                msg = MIMEMultipart("alternative")
                msg.attach(MIMEText(text_body, "plain", "utf-8"))
                msg.attach(MIMEText(html_body, "html", "utf-8"))
        else:
            msg = MIMEText(text_body, "plain", "utf-8")
        msg["Subject"] = Header(subject, "utf-8")
        msg["From"] = formataddr((str(Header("HogarFix", "utf-8")), from_email))
        msg["To"] = to_email

        try:
            if smtp_use_ssl:
                with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=timeout_secs) as server:
                    server.login(smtp_username, smtp_password)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(smtp_host, smtp_port, timeout=timeout_secs) as server:
                    if smtp_use_tls:
                        server.starttls()
                    server.login(smtp_username, smtp_password)
                    server.send_message(msg)
            return True, "sent"
        except Exception as exc:
            current_app.logger.warning("Email send failed: %s", exc)
            return False, "mail-error"

    if backend in {"api", "mailersend_api"}:
        api_token = current_app.config.get("MAIL_API_TOKEN", "")
        api_url = current_app.config.get("MAIL_API_URL", "https://api.mailersend.com/v1/email")
        from_name = current_app.config.get("MAIL_FROM_NAME", "HogarFix")

        if not api_token or not from_email:
            return False, "mail-api-missing-config"

        payload = {
            "from": {"email": from_email, "name": from_name},
            "to": [{"email": to_email}],
            "subject": subject,
            "text": text_body,
        }
        if html_body:
            payload["html"] = html_body

        if html_body and f"cid:{MAIL_LOGO_CID}" in html_body:
            logo_path, logo_name, _logo_type = _mail_local_logo_asset()
            if logo_path:
                with open(logo_path, "rb") as logo_file:
                    encoded_logo = base64.b64encode(logo_file.read()).decode("ascii")

                payload["attachments"] = [
                    {
                        "filename": logo_name,
                        "content": encoded_logo,
                        "disposition": "inline",
                        "id": MAIL_LOGO_CID,
                    }
                ]

        req = urlrequest.Request(
            api_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "HogarFixMailer/1.0",
                "X-Requested-With": "HogarFix",
            },
            method="POST",
        )

        try:
            with urlrequest.urlopen(req, timeout=timeout_secs) as resp:
                if resp.status in {200, 201, 202}:
                    return True, "sent-api"
                current_app.logger.warning("Mail API unexpected status: %s", resp.status)
                smtp_ok, smtp_status = _send_via_smtp()
                if smtp_ok:
                    return True, "sent-smtp-fallback"
                return False, "mail-api-error"
        except urlerror.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="ignore") if exc.fp else ""
            current_app.logger.warning("Mail API HTTP error: %s %s", exc.code, body)
            smtp_ok, smtp_status = _send_via_smtp()
            if smtp_ok:
                return True, "sent-smtp-fallback"
            return False, "mail-api-error"
        except Exception as exc:
            current_app.logger.warning("Mail API send failed: %s", exc)
            smtp_ok, smtp_status = _send_via_smtp()
            if smtp_ok:
                return True, "sent-smtp-fallback"
            return False, "mail-api-error"

    if backend == "file":
        try:
            file_path = current_app.config.get("MAIL_FILE_PATH", os.path.join("app", "mail_outbox.log"))
            if not os.path.isabs(file_path):
                file_path = os.path.join(current_app.root_path, "..", file_path)

            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "a", encoding="utf-8") as outbox:
                outbox.write("\n" + "=" * 72 + "\n")
                outbox.write(f"timestamp: {datetime.utcnow().isoformat()}Z\n")
                outbox.write(f"subject: {subject}\n")
                outbox.write(f"from: {from_email}\n")
                outbox.write(f"to: {to_email}\n")
                outbox.write("\n[text]\n")
                outbox.write(text_body.strip() + "\n")
                if html_body:
                    outbox.write("\n[html]\n")
                    outbox.write(html_body.strip() + "\n")
            return True, "sent-file"
        except Exception as exc:
            current_app.logger.warning("Email file backend failed: %s", exc)
            return False, "mail-file-error"

    return _send_via_smtp()


def _mail_brand_header():
    logo_url = (current_app.config.get("MAIL_LOGO_URL", "") or "").strip()

    # Email clients require absolute URLs; resolve ./ and ../ paths when configured.
    if logo_url and not logo_url.startswith(("http://", "https://", "data:", "cid:")):
        base_url = (current_app.config.get("MAIL_PUBLIC_BASE_URL", "") or "").strip().rstrip("/")
        if not base_url and has_request_context():
            base_url = request.host_url.rstrip("/")
        if base_url:
            logo_url = urljoin(f"{base_url}/", logo_url)

    if logo_url:
        return (
            "<img src='{}' alt='HogarFix' style='height:44px;display:block;margin:0 auto 12px auto;'>".format(
                logo_url
            )
        )

    logo_path, _, _ = _mail_local_logo_asset()
    if logo_path:
        return (
            "<div style='display:inline-flex;align-items:center;justify-content:center;"
            "background:#ffffff;border-radius:18px;padding:10px 18px;margin:0 auto 14px auto;"
            "box-shadow:0 8px 24px rgba(9,30,66,.16);'>"
            "<img src='cid:{}' alt='HogarFix' "
            "style='height:74px;display:block;'>"
            "</div>"
        ).format(MAIL_LOGO_CID)

    return (
        "<div style='text-align:center;margin:0 auto 12px auto;'>"
        "<span style='display:inline-block;background:#0a2540;color:#ffffff;font-weight:800;"
        "font-size:20px;border-radius:10px;padding:8px 14px;letter-spacing:.2px;'>"
        "HogarFix"
        "</span>"
        "</div>"
    )


def _mail_shell(title, intro_html, body_html, accent="#0a2540"):
        base_url = (current_app.config.get("MAIL_PUBLIC_BASE_URL", "") or "").strip().rstrip("/")
        social_links = []
        social_map = [
            ("Facebook", (current_app.config.get("MAIL_FACEBOOK_URL", "") or "").strip()),
            ("Instagram", (current_app.config.get("MAIL_INSTAGRAM_URL", "") or "").strip()),
            ("LinkedIn", (current_app.config.get("MAIL_LINKEDIN_URL", "") or "").strip()),
            ("YouTube", (current_app.config.get("MAIL_YOUTUBE_URL", "") or "").strip()),
        ]
        for label, url in social_map:
            if url:
                social_links.append(
                    f"<a href='{url}' style='color:#4f6f89;text-decoration:none;font-size:12px;margin:0 6px;'>{label}</a>"
                )
        social_html = "".join(social_links) if social_links else ""
        web_html = (
            f"<p style='margin:0 0 8px 0;font-size:12px;color:#6f879f;'>Sitio web: <a href='{base_url}' style='color:#31597c;text-decoration:none;'>{base_url}</a></p>"
            if base_url
            else ""
        )

        return f"""
        <html>
            <body style='margin:0;padding:28px;background:#edf3f9;font-family:Arial,sans-serif;color:#10243b;'>
                <div style='max-width:640px;margin:0 auto;background:#ffffff;border:1px solid #d8e6f3;border-radius:16px;overflow:hidden;box-shadow:0 8px 24px rgba(18,36,59,.08);'>
                    <div style='background:linear-gradient(120deg,{accent},#1d4b78);padding:20px 22px;color:#ffffff;'>
                        <div style='text-align:center;'>{_mail_brand_header()}</div>
                        <div style='text-align:center;font-size:18px;font-weight:800;letter-spacing:.02em;margin:0 0 10px 0;color:#ffffff;'>HogarFix</div>
                        <h2 style='margin:0;font-size:28px;line-height:1.2;text-align:center;color:#ffffff;'>{title}</h2>
                    </div>
                    <div style='padding:24px 24px 22px 24px;'>
                        <p style='margin:0 0 14px 0;font-size:18px;line-height:1.55;'>{intro_html}</p>
                        {body_html}
                        <p style='margin:28px 0 10px 0;color:#55718b;font-size:14px;line-height:1.5;'>Equipo HogarFix</p>
                    </div>
                    <div style='border-top:1px solid #e3edf7;background:#f7fbff;padding:14px 18px;text-align:center;'>
                        {web_html}
                        {social_html}
                        <p style='margin:8px 0 0 0;font-size:11px;color:#8aa0b4;'>Copyright {datetime.utcnow().year} HogarFix. Todos los derechos reservados.</p>
                    </div>
                </div>
            </body>
        </html>
        """


def send_otp_code_email(to_email, otp_code, ttl_minutes=3):
    subject = "Tu codigo de verificacion HogarFix"
    text_body = (
        f"Tu codigo de verificacion es: {otp_code}. "
        f"Expira en {ttl_minutes} minutos.\n\n"
        "Si no intentaste iniciar sesion, ignora este mensaje."
    )
    intro_html = "Recibimos una solicitud de inicio de sesion y debemos confirmar tu identidad."
    body_html = (
        "<div style='background:#f8fbff;border:1px solid #d8e8f8;border-radius:14px;padding:16px 18px;text-align:center;'>"
        "<p style='margin:0 0 10px 0;color:#31597c;font-size:13px;font-weight:700;'>CODIGO DE VERIFICACION</p>"
        f"<p style='margin:0 0 10px 0;font-size:34px;letter-spacing:6px;font-weight:800;color:#0a2540;'>{otp_code}</p>"
        f"<p style='margin:0;color:#4f6f89;font-size:13px;'>Valido por {ttl_minutes} minutos.</p>"
        "</div>"
        "<div style='margin-top:14px;background:#fff7ed;border:1px solid #ffd7b3;border-radius:12px;padding:12px 14px;'>"
        "<p style='margin:0;font-size:13px;line-height:1.55;color:#6a4b2f;'>Por seguridad, no compartas este codigo con nadie.</p>"
        "</div>"
    )
    html_body = _mail_shell("Codigo de verificacion", intro_html, body_html, accent="#0a2540")
    return send_email(subject=subject, to_email=to_email, text_body=text_body, html_body=html_body)


def send_welcome_email(to_email, full_name):
    name = full_name or "usuario"
    subject = "Bienvenido a HogarFix: cuenta activa"
    body = (
        f"Hola {name},\n\n"
        "Tu cuenta en HogarFix se creo correctamente y ya esta activa.\n"
        "Ahora puedes iniciar sesion y gestionar tus solicitudes de servicio.\n\n"
        "Recomendaciones:\n"
        "- Mantener tu contrasena en privado\n"
        "- Revisar tus datos de perfil\n"
        "- Activar notificaciones de actividad\n\n"
        "Equipo HogarFix"
    )

    intro_html = f"Hola <strong>{name}</strong>, tu cuenta fue creada correctamente y ya se encuentra activa."
    body_html = (
        "<div style='background:#f8fbff;border:1px solid #d8e8f8;border-radius:14px;padding:16px 18px;'>"
        "<p style='margin:0 0 10px 0;line-height:1.55;color:#13314f;'>"
        "Tu acceso esta listo. Desde este momento puedes iniciar sesion y usar todas las funciones de la plataforma."
        "</p>"
        "<div style='background:#ffffff;border:1px solid #dfeaf5;border-radius:10px;padding:10px 12px;'>"
        "<p style='margin:0 0 8px 0;font-size:12px;font-weight:700;color:#31597c;'>SIGUIENTE PASO RECOMENDADO</p>"
        "<p style='margin:0;color:#4f6f89;font-size:13px;line-height:1.5;'>Completa tu perfil para recibir una experiencia mas personalizada y segura.</p>"
        "</div>"
        "</div>"
        "<div style='margin-top:14px;background:#eef7ff;border:1px solid #cfe6fb;border-radius:12px;padding:12px 14px;'>"
        "<p style='margin:0 0 7px 0;font-size:13px;font-weight:700;color:#1f557f;'>Buenas practicas de seguridad</p>"
        "<p style='margin:0;font-size:13px;line-height:1.55;color:#3f627e;'>No compartas tus credenciales y evita iniciar sesion desde dispositivos publicos.</p>"
        "</div>"
        "<p style='margin:14px 0 0 0;line-height:1.55;color:#4f6f89;'>Gracias por confiar en HogarFix.</p>"
        "</div>"
    )
    html_body = _mail_shell("Bienvenido a HogarFix", intro_html, body_html, accent="#0a2540")
    return send_email(subject=subject, to_email=to_email, text_body=body, html_body=html_body)


def send_login_alert_email(to_email, full_name, ip_address, user_agent, login_at=None):
        name = full_name or "usuario"
        when = (login_at or datetime.utcnow()).strftime("%Y-%m-%d %H:%M UTC")
        safe_ip = ip_address or "No disponible"
        safe_agent = user_agent or "No disponible"

        subject = "Alerta de seguridad: actividad de inicio de sesion"
        body = (
                f"Hola {name},\n\n"
                "Detectamos un inicio de sesion desde un dispositivo o red diferente a los habituales.\n"
                f"Fecha y hora: {when}\n"
                f"IP: {safe_ip}\n"
                f"Dispositivo/Navegador: {safe_agent}\n\n"
                "Si reconoces esta actividad, no es necesario hacer cambios.\n"
                "Si no la reconoces, cambia tu contrasena de inmediato y contacta soporte.\n\n"
                "Equipo de Seguridad HogarFix"
        )

        intro_html = (
            f"Hola <strong>{name}</strong>, detectamos una actividad de inicio de sesion fuera de lo habitual."
        )
        body_html = (
            "<div style='background:#fff4f5;border:1px solid #f8c9cf;border-radius:14px;padding:16px 18px;'>"
            "<p style='margin:0 0 10px 0;line-height:1.55;color:#611b25;font-weight:700;'>"
            "Detalle del evento detectado"
            "</p>"
            "<div style='background:#ffffff;border:1px solid #f2d7db;border-radius:10px;padding:10px 12px;'>"
            f"<p style='margin:0 0 8px 0;line-height:1.55;color:#5c2c35;'><strong>Fecha y hora:</strong> {when}</p>"
            f"<p style='margin:0 0 8px 0;line-height:1.55;color:#5c2c35;'><strong>IP:</strong> {safe_ip}</p>"
            f"<p style='margin:0;line-height:1.55;color:#5c2c35;'><strong>Dispositivo/Navegador:</strong> {safe_agent}</p>"
            "</div>"
            "</div>"
            "<div style='margin-top:14px;background:#fff7ed;border:1px solid #ffd7b3;border-radius:12px;padding:12px 14px;'>"
            "<p style='margin:0 0 7px 0;font-size:13px;font-weight:700;color:#8b4c0e;'>Accion recomendada</p>"
            "<p style='margin:0;font-size:13px;line-height:1.55;color:#6a4b2f;'>Si no reconoces este acceso, cambia tu contrasena cuanto antes y revisa tu actividad reciente.</p>"
            "</div>"
        )
        html_body = _mail_shell("Alerta de seguridad", intro_html, body_html, accent="#9f1239")

        return send_email(subject=subject, to_email=to_email, text_body=body, html_body=html_body)


def send_password_reset_email(to_email, full_name, reset_url):
        name = full_name or "usuario"
        subject = "Accion requerida: restablecer contrasena"
        body = (
                f"Hola {name},\n\n"
                "Recibimos una solicitud para restablecer la contrasena de tu cuenta HogarFix.\n"
                "Este enlace es de un solo uso y expira en 1 hora.\n\n"
                f"Abrir enlace seguro: {reset_url}\n\n"
                "Si no solicitaste este cambio, ignora este mensaje y no compartas este enlace.\n\n"
                "Equipo de Seguridad HogarFix"
        )

        intro_html = (
            f"Hola <strong>{name}</strong>, recibimos una solicitud para restablecer la contrasena de tu cuenta."
        )
        body_html = (
            "<div style='background:#f8fbff;border:1px solid #d8e8f8;border-radius:14px;padding:16px 18px;'>"
            "<p style='margin:0 0 12px 0;line-height:1.55;color:#13314f;'>"
            "Para continuar con seguridad, confirma la accion desde el siguiente boton."
            "</p>"
            f"<p style='margin:0 0 14px 0;'><a href='{reset_url}' style='display:inline-block;background:#0a2540;color:#ffffff;text-decoration:none;padding:11px 18px;border-radius:10px;font-weight:700;letter-spacing:.01em;'>Restablecer contrasena</a></p>"
            "<div style='background:#ffffff;border:1px dashed #b8d3ea;border-radius:10px;padding:10px 12px;'>"
            "<p style='margin:0 0 6px 0;font-size:12px;font-weight:700;color:#31597c;'>ENLACE DIRECTO</p>"
            f"<p style='margin:0;font-size:12px;line-height:1.45;color:#55718b;word-break:break-all;'>{reset_url}</p>"
            "</div>"
            "</div>"
            "<div style='margin-top:14px;background:#fff7ed;border:1px solid #ffd7b3;border-radius:12px;padding:12px 14px;'>"
            "<p style='margin:0 0 7px 0;font-size:13px;font-weight:700;color:#8b4c0e;'>Recomendaciones de seguridad</p>"
            "<p style='margin:0;font-size:13px;line-height:1.55;color:#6a4b2f;'>"
            "1) Este enlace expira en 1 hora. 2) Solo funciona una vez. 3) No lo compartas con terceros."
            "</p>"
            "</div>"
            "<p style='margin:14px 0 0 0;line-height:1.55;color:#4f6f89;'>"
            "Si no solicitaste este cambio, puedes ignorar este mensaje. Tu cuenta seguira protegida."
            "</p>"
        )
        html_body = _mail_shell("Recuperacion de contrasena", intro_html, body_html, accent="#0a2540")

        return send_email(subject=subject, to_email=to_email, text_body=body, html_body=html_body)
