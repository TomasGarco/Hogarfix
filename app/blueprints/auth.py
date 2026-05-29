from datetime import datetime, timedelta
import json
import os
import secrets
from urllib.parse import urljoin

from flask import Blueprint, current_app, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user
from itsdangerous import BadData, SignatureExpired, URLSafeTimedSerializer
import re

try:
    from authlib.integrations.base_client.errors import OAuthError
except ModuleNotFoundError:
    class OAuthError(Exception):
        pass

from app.extensions import db, oauth
from app.extensions import limiter
from app.models import LoginLog, TechnicianProfile, User, UserSession
from app.services.email import send_email
from app.services.identity_verification import verify_identity
from app.services.otp import (
    clear_otp_for_user,
    get_active_otp,
    issue_otp_for_user,
    resend_otp_for_user,
    verify_otp_for_user,
)
from app.utils import send_login_alert_email, send_otp_code_email, send_password_reset_email, send_welcome_email, save_upload


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

WELCOME_MESSAGES = {
    "cliente": "Iniciaste sesion como cliente.",
    "tecnico": "Iniciaste sesion como tecnico.",
    "admin": "Iniciaste sesion como admin.",
}

REGISTER_MESSAGES = {
    "cliente": "Te registraste como cliente.",
    "tecnico": "Te registraste como tecnico.",
}


def _get_serializer():
    return URLSafeTimedSerializer(auth_bp.root_path + "-hogarfix-reset")


def _is_strong_password(password: str) -> bool:
    if len(password) < 8:
        return False
    has_upper = bool(re.search(r"[A-Z]", password))
    has_lower = bool(re.search(r"[a-z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_special = bool(re.search(r"[^A-Za-z0-9]", password))
    # Block weak patterns: repeated digits/letters, common weak passwords
    weak_patterns = {
        '11111111', '22222222', '33333333', '44444444', '55555555', '66666666', '77777777', '88888888', '99999999', '00000000',
        '12345678', '87654321', 'password', 'contraseña', 'qwerty', 'asdfgh', 'hogarfix', 'abcdefgh', 'abc12345',
    }
    clean = password.lower()
    if clean in weak_patterns:
        return False
    # All digits or all letters repeated
    if re.fullmatch(r'([0-9])\1{7,}', password):
        return False
    if re.fullmatch(r'([a-zA-Z])\1{7,}', password):
        return False
    # Only numbers
    if re.fullmatch(r'\d{8,}', password):
        return False
    # Only one character repeated
    if re.fullmatch(r'([a-zA-Z0-9])\1+', password):
        return False
    return has_upper and has_lower and has_digit and has_special


def _get_rotating_code(base_env_name: str, fallback_value: str = "") -> str:
    month_key = datetime.utcnow().strftime("%Y%m")
    monthly_name = f"{base_env_name}_{month_key}"
    return (os.environ.get(monthly_name) or os.environ.get(base_env_name) or fallback_value or "").strip()


def _validate_admin_security_code(
    submitted_code: str,
    code_env_name: str,
    fallback_code: str,
    session_prefix: str,
    not_configured_message: str,
):
    now_ts = datetime.utcnow().timestamp()
    max_attempts = int(current_app.config.get("ADMIN_SECURITY_MAX_ATTEMPTS", 3) or 3)
    block_minutes = int(current_app.config.get("ADMIN_SECURITY_BLOCK_MINUTES", 15) or 15)

    attempts_key = f"{session_prefix}_attempts"
    block_key = f"{session_prefix}_block_until"

    blocked_until = float(session.get(block_key, 0) or 0)
    if blocked_until > now_ts:
        wait_seconds = int(blocked_until - now_ts)
        return False, f"Acceso admin bloqueado temporalmente. Intenta de nuevo en {wait_seconds} segundos."

    expected_code = _get_rotating_code(code_env_name, fallback_code)
    if not expected_code:
        return False, not_configured_message

    if submitted_code != expected_code:
        attempts = int(session.get(attempts_key, 0) or 0) + 1
        session[attempts_key] = attempts

        if attempts >= max_attempts:
            session[attempts_key] = 0
            session[block_key] = (datetime.utcnow() + timedelta(minutes=block_minutes)).timestamp()
            return False, (
                f"Superaste {max_attempts} intentos con la contrasena de seguridad. "
                f"Acceso bloqueado por {block_minutes} minutos."
            )

        remaining = max_attempts - attempts
        return False, f"Contrasena de seguridad invalida. Te quedan {remaining} intento(s)."

    session[attempts_key] = 0
    session[block_key] = 0
    return True, ""


def _normalize_address(value: str) -> str:
    out = re.sub(r"\s+", " ", (value or "").strip())
    replacements = (
        (r"^(carrera|cra|kr)\s*(\d)", r"Cra \2"),
        (r"^(calle|cl|cll)\s*(\d)", r"Cll \2"),
        (r"^(avenida|av)\s*(\d)", r"Av \2"),
        (r"^(diagonal|dg)\s*(\d)", r"Dg \2"),
        (r"^(transversal|transv|tv)\s*(\d)", r"Tv \2"),
    )
    for pattern, replacement in replacements:
        out = re.sub(pattern, replacement, out, flags=re.IGNORECASE)
    out = re.sub(r"(\d)(#)", r"\1 #", out)
    out = re.sub(r"(#)(\d)", r"# \2", out)
    out = re.sub(r"(\d)-(\d)", r"\1 - \2", out)
    out = re.sub(r"\s*#\s*", " # ", out)
    out = re.sub(r"\s*-\s*", " - ", out)
    out = re.sub(r"(\d)([a-z])", lambda match: f"{match.group(1)}{match.group(2).upper()}", out, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", out).strip()


def _normalize_person_name(value: str) -> str:
    text = re.sub(r"\s+", " ", (value or "").strip())
    if not text:
        return ""
    return " ".join(part.capitalize() for part in text.split(" "))


def _normalize_text_title(value: str) -> str:
    text = re.sub(r"\s+", " ", (value or "").strip())
    if not text:
        return ""
    return text[0].upper() + text[1:]


def _send_login_otp_email(to_email: str, code: str):
    ttl_minutes = int(current_app.config.get("OTP_TTL_MINUTES", 3))
    # Simulacion de envio para desarrollo/local.
    print(f"[OTP DEBUG] destino={to_email} codigo={code} expira_en={ttl_minutes}m")
    return send_otp_code_email(to_email=to_email, otp_code=code, ttl_minutes=ttl_minutes)


def _build_public_url(endpoint: str, **values) -> str:
    public_base = (current_app.config.get("MAIL_PUBLIC_BASE_URL", "") or "").strip().rstrip("/")
    relative_path = url_for(endpoint, **values, _external=False)
    if public_base:
        return urljoin(f"{public_base}/", relative_path.lstrip("/"))
    return url_for(endpoint, **values, _external=True)


def _create_oauth_redirect_uri(config_key: str, endpoint: str) -> str:
    configured = (current_app.config.get(config_key, "") or "").strip()
    if configured:
        return configured
    return url_for(endpoint, _external=True)


def _social_login_enabled(provider: str) -> bool:
    if oauth is None or not current_app.config.get("SOCIAL_AUTH_AVAILABLE"):
        return False
    return oauth.create_client(provider) is not None


def _build_social_identity(provider: str, token: dict, nonce: str | None) -> dict:
    if oauth is None or not current_app.config.get("SOCIAL_AUTH_AVAILABLE"):
        raise ValueError("El inicio de sesion social no esta disponible en este entorno.")

    client = oauth.create_client(provider)
    if client is None:
        raise ValueError("El proveedor social no esta configurado.")

    claims = client.parse_id_token(token, nonce=nonce) if nonce else {}

    if provider == "google":
        email = (claims.get("email") or "").strip().lower()
        if not email:
            raise ValueError("Google no devolvio un correo valido para esta cuenta.")
        if claims.get("email_verified") is False:
            raise ValueError("Tu cuenta de Google debe tener el correo verificado para continuar.")
        return {
            "email": email,
            "name": (claims.get("name") or "").strip(),
            "avatar": (claims.get("picture") or "").strip() or None,
            "subject": (claims.get("sub") or "").strip(),
        }

    profile = {}
    try:
        response = client.get("https://graph.microsoft.com/v1.0/me")
        if response is not None:
            profile = response.json() or {}
    except Exception:
        profile = {}

    email = (
        (profile.get("mail") or "").strip()
        or (profile.get("userPrincipalName") or "").strip()
        or (claims.get("preferred_username") or "").strip()
        or (claims.get("email") or "").strip()
    ).lower()

    if not email:
        raise ValueError("Microsoft no devolvio un correo valido para esta cuenta.")

    return {
        "email": email,
        "name": (profile.get("displayName") or claims.get("name") or "").strip(),
        "avatar": None,
        "subject": (claims.get("sub") or "").strip(),
    }


def _find_or_create_social_user(provider: str, identity: dict) -> tuple[User, bool]:
    email = (identity.get("email") or "").strip().lower()
    full_name = _normalize_person_name(identity.get("name") or "")
    avatar_url = identity.get("avatar") or None
    subject = (identity.get("subject") or "").strip()

    linked_user = None
    if subject:
        linked_user = User.query.filter_by(oauth_provider=provider, oauth_subject=subject).first()

    user = linked_user or User.query.filter_by(email=email).first()
    created = False

    if linked_user and user and linked_user.id != user.id:
        raise ValueError("Esta cuenta social ya esta vinculada a otro usuario.")

    if user and user.role == "admin":
        raise ValueError("Las cuentas admin no pueden iniciar sesion con proveedores sociales.")

    # Si el usuario NO existe, bloquear el registro automático y pedir registro manual
    if user is None:
        raise ValueError("Primero debes registrarte con tu correo y contraseña antes de usar Google.")

    # Si existe, actualizar datos sociales si aplica
    if full_name and not user.full_name:
        user.full_name = full_name
    if avatar_url:
        user.avatar_url = avatar_url
    user.oauth_provider = provider
    user.oauth_subject = subject or user.oauth_subject

    db.session.commit()
    return user, created


def _register_active_session(user: User):
    session_token = secrets.token_hex(24)
    current_ip = request.remote_addr or ""
    current_user_agent = (request.user_agent.string or "")[:255]

    session_record = UserSession(
        user_id=user.id,
        session_token=session_token,
        ip_address=current_ip,
        user_agent=current_user_agent,
    )
    db.session.add(session_record)
    db.session.flush()
    session["active_session_token"] = session_token


def _finish_successful_login(user: User):
    previous_log = LoginLog.query.filter_by(user_id=user.id).order_by(LoginLog.login_at.desc()).first()
    current_ip = request.remote_addr or ""
    current_user_agent = (request.user_agent.string or "")[:255]

    login_user(user)
    session["user_id"] = user.id
    session["2fa_ok"] = True
    session.pop("pre_2fa_user_id", None)
    session.pop("pre_2fa_login_as", None)
    _register_active_session(user)

    log = LoginLog(
        user_id=user.id,
        ip_address=current_ip,
        user_agent=current_user_agent,
    )
    db.session.add(log)
    db.session.commit()

    unusual_login = False
    if previous_log:
        ip_changed = bool(previous_log.ip_address) and bool(current_ip) and previous_log.ip_address != current_ip
        ua_changed = (
            bool(previous_log.user_agent)
            and bool(current_user_agent)
            and previous_log.user_agent != current_user_agent
        )
        unusual_login = ip_changed or ua_changed

    if unusual_login:
        display_name = user.email.split("@")[0]
        if user.role == "tecnico" and user.technician_profile and user.technician_profile.full_name:
            display_name = user.technician_profile.full_name
        send_login_alert_email(
            to_email=user.email,
            full_name=display_name,
            ip_address=current_ip,
            user_agent=current_user_agent,
            login_at=log.login_at,
        )

    flash(WELCOME_MESSAGES.get(user.role, "Bienvenido a HogarFix."), "info")
    return redirect(url_for("main.dashboard"))


def _start_otp_login_challenge(user: User, login_as: str):
    _, otp_code = issue_otp_for_user(user.id, channel="email")
    email_sent, _email_status = _send_login_otp_email(user.email, otp_code)

    session.pop("2fa_ok", None)
    session.pop("user_id", None)
    session["pre_2fa_user_id"] = user.id
    session["pre_2fa_login_as"] = login_as

    if not email_sent:
        current_app.logger.warning(
            "[OTP] Email delivery issue for user %s (%s) — status: %s",
            user.id, user.email, _email_status,
        )
    flash("Te enviamos un codigo de 6 digitos a tu correo. Ingresalo para continuar.", "info")
    return redirect(url_for("auth.verify_otp"))


@auth_bp.route("/contrato-preview.pdf")
def contrato_preview():
    """Genera un PDF de muestra del contrato para que el técnico lo lea antes de registrarse."""
    from app.services.contract_pdf import generar_contrato_pdf

    class _FakeUser:
        id = 0
        full_name = "[Tu nombre completo]"
        email = "tecnico@ejemplo.com"
        phone = "300 000 0000"
        phone_country = "+57"
        locality = "Bogotá"
        barrio = "[Tu barrio]"
        address = "[Tu dirección]"

    class _FakeProfile:
        full_name = "[Tu nombre completo]"
        bio = None
        specialties = "Electricidad, Plomería"
        localities = "Bogotá"
        price_range = "hora:50000"
        verification_status = "pendiente"

    pdf_bytes = generar_contrato_pdf(_FakeUser(), _FakeProfile())
    return current_app.response_class(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": "inline; filename=contrato-hogarfix.pdf"},
    )


@auth_bp.route("/register", methods=["GET", "POST"])
@limiter.limit("5 per minute; 20 per hour", methods=["POST"])
def register():
    _OBVIOUS_SEQUENCES = {
        "111111", "1111111", "11111111", "222222", "2222222", "22222222",
        "333333", "3333333", "33333333", "444444", "4444444", "44444444",
        "555555", "5555555", "55555555", "666666", "6666666", "66666666",
        "777777", "7777777", "77777777", "888888", "8888888", "88888888",
        "999999", "9999999", "99999999", "000000", "0000000", "00000000",
        "123456", "1234567", "12345678", "987654", "9876543", "98765432",
        "aaaaaa", "bbbbbb", "cccccc", "test", "prueba", "nombre", "apellido",
    }

    def is_repetitive_or_numeric(val):
        clean = (val or "").replace(" ", "").lower()
        if not clean:
            return False
        # Solo un dígito o letra repetida
        if len(set(clean)) == 1:
            return True
        # Secuencias conocidas
        if clean in _OBVIOUS_SEQUENCES:
            return True
        # Solo dígitos
        if clean.isdigit():
            return True
        # Solo un carácter repetido (ej: aaaaa)
        if re.fullmatch(r"([a-z0-9])\1+", clean):
            return True
        return False

    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        account_type = request.form.get("account_type", "cliente").strip().lower()
        first_name = _normalize_person_name(request.form.get("first_name", ""))
        last_name = _normalize_person_name(request.form.get("last_name", ""))
        specialty = _normalize_text_title(request.form.get("specialty", ""))
        services_selected = [s.strip() for s in request.form.getlist("services") if s.strip()]
        years_experience = request.form.get("years_experience", "").strip()
        service_description = _normalize_text_title(request.form.get("service_description", ""))
        document_type = request.form.get("document_type", "").strip().lower()
        document_number = request.form.get("document_number", "").strip()
        charge_type = request.form.get("charge_type", "").strip().lower()
        identity_provider = (
            request.form.get("identity_provider", "").strip().lower()
            or current_app.config.get("IDENTITY_PROVIDER", "mock")
        )
        base_price = request.form.get("base_price", "").strip()
        availability_days = [d.strip() for d in request.form.getlist("availability_days") if d.strip()]
        start_time = request.form.get("availability_start", "").strip()
        end_time = request.form.get("availability_end", "").strip()
        signature_data = request.form.get("signature_data", "").strip()
        technician_address = _normalize_address(request.form.get("technician_address", ""))
        geo_lat = request.form.get("geo_lat", "").strip()
        geo_lng = request.form.get("geo_lng", "").strip()
        full_name = f"{first_name} {last_name}".strip()
        phone = request.form.get("phone", "").strip()
        phone_country = request.form.get("phone_country", "+57").strip()
        locality = _normalize_person_name(request.form.get("locality", ""))
        barrio = _normalize_person_name(request.form.get("barrio", ""))
        client_address = _normalize_address(request.form.get("client_address", ""))
        # carrera eliminado
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        accepted_terms = request.form.get("accepted_terms") == "on"
        normalized_phone = re.sub(r"\D", "", phone)
        phone_rules = {
            "+57": 10,
            "+1": 10,
            "+52": 10,
            "+51": 9,
            "+593": 9,
            "+54": 10,
            "+56": 9,
            "+34": 9,
        }
        expected_phone_length = phone_rules.get(phone_country, 10)

        if account_type not in {"cliente", "tecnico"}:
            account_type = "cliente"

        role = account_type

        def _err(msg):
            return render_template("auth/register.html", type=account_type, error=msg, form=request.form)

        # --- Campos obligatorios comunes ---
        missing_fields = []
        if not first_name:
            missing_fields.append("nombre")
        if not last_name:
            missing_fields.append("apellido")
        if not phone:
            missing_fields.append("teléfono")
        if not locality:
            missing_fields.append("localidad")
        if not barrio:
            missing_fields.append("barrio")
        if not email:
            missing_fields.append("email")
        if not password:
            missing_fields.append("contraseña")
        if not confirm_password:
            missing_fields.append("confirmar contraseña")

        # --- Campos obligatorios por tipo ---
        if account_type == "cliente" and not client_address:
            missing_fields.append("dirección")

        if account_type == "tecnico":
            if not specialty:
                missing_fields.append("categoría principal")
            if not years_experience:
                missing_fields.append("años de experiencia")
            if not service_description:
                missing_fields.append("descripción de servicios")
            if not document_type:
                missing_fields.append("tipo de documento")
            if not document_number:
                missing_fields.append("número de documento")
            if not technician_address:
                missing_fields.append("dirección")
            if not charge_type:
                missing_fields.append("tipo de cobro")
            if not base_price:
                missing_fields.append("precio base")
            if not availability_days:
                missing_fields.append("días de disponibilidad")
            if not start_time or not end_time:
                missing_fields.append("rango horario")
            if not signature_data:
                missing_fields.append("firma")

        if missing_fields:
            return _err("Por favor completa: " + ", ".join(missing_fields) + ".")

        # --- Validación datos repetitivos / solo numéricos ---
        if is_repetitive_or_numeric(first_name):
            return _err("El nombre no puede ser solo números o datos repetitivos (ej: 111111, aaaa).")
        if is_repetitive_or_numeric(last_name):
            return _err("El apellido no puede ser solo números o datos repetitivos.")
        if is_repetitive_or_numeric(barrio):
            return _err("El barrio no puede ser solo números o datos repetitivos.")
        phone_digits = re.sub(r'\D', '', phone or '')
        if phone_digits and re.fullmatch(r'([0-9])\1+', phone_digits):
            return _err("El teléfono no puede ser todos los dígitos iguales o repetitivos.")
        if is_repetitive_or_numeric(email.split("@")[0]):
            return _err("El email no puede tener solo números o caracteres repetitivos.")
        if account_type == "cliente" and is_repetitive_or_numeric(client_address):
            return _err("La dirección no puede ser solo números o datos repetitivos.")
        if account_type == "tecnico":
            doc_clean = re.sub(r"[\s\-]", "", document_number)
            if doc_clean and (
                len(set(doc_clean)) == 1
                or doc_clean in _OBVIOUS_SEQUENCES
                or re.fullmatch(r"([a-z0-9])\1+", doc_clean.lower())
            ):
                return _err("El número de documento no puede ser datos repetitivos.")
            if is_repetitive_or_numeric(service_description):
                return _err("La descripción de servicios no puede ser datos repetitivos.")
            if is_repetitive_or_numeric(technician_address):
                return _err("La dirección del técnico no puede ser datos repetitivos.")

        # --- Términos y condiciones ---
        if not accepted_terms:
            return _err("Debes aceptar los Términos y Condiciones y la Política de Privacidad para crear tu cuenta.")

        # --- Teléfono: longitud exacta ---
        if len(normalized_phone) != expected_phone_length:
            return _err(
                f"El teléfono para {phone_country} debe tener exactamente {expected_phone_length} dígitos."
            )

        # --- Contraseña segura ---
        if not _is_strong_password(password):
            return _err(
                "La contraseña debe tener mínimo 8 caracteres, una mayúscula, una minúscula, un número y un carácter especial."
            )

        if password != confirm_password:
            return _err("Las contraseñas no coinciden.")

        if User.query.filter_by(email=email).first():
            return _err("Ese email ya está registrado. ¿Ya tienes cuenta?")

        user = User(email=email, role=role)
        user.set_password(password)
        user.full_name = full_name
        user.phone = normalized_phone
        user.phone_country = phone_country
        user.locality = locality
        user.barrio = barrio or None
        user.address = client_address if account_type == "cliente" else technician_address
        # user.carrera eliminado
        user.accepted_terms = True
        user.accepted_terms_at = datetime.utcnow()
        db.session.add(user)
        db.session.flush()

        technician_verification_status = ""
        technician_verification_reason = ""

        if role == "tecnico":
            locality_text = f"{locality} - {barrio}" if barrio else locality
            full_phone = f"{phone_country} {normalized_phone}"
            verification_front = save_upload(request.files.get("document_front"), "verification")
            verification_back = save_upload(request.files.get("document_back"), "verification")
            verification_selfie = save_upload(request.files.get("selfie_file"), "verification")
            certification_file = save_upload(request.files.get("certifications_file"), "verification")

            work_photos = []
            for file_item in request.files.getlist("portfolio_files"):
                saved_file = save_upload(file_item, "work")
                if saved_file:
                    work_photos.append(saved_file)

            profile_meta = {
                "document_type": document_type,
                "document_number": document_number,
                "service_description": service_description,
                "charge_type": charge_type,
                "identity_provider": identity_provider,
                "base_price": base_price,
                "availability_days": availability_days,
                "availability_start": start_time,
                "availability_end": end_time,
                "signature_data": signature_data,
                "services": services_selected,
                "technician_address": technician_address,
                "geo_lat": geo_lat,
                "geo_lng": geo_lng,
                "certification_file": certification_file,
                "contact_phone": full_phone,
            }

            verification_front_url = (
                url_for("static", filename=verification_front, _external=True) if verification_front else ""
            )
            verification_back_url = (
                url_for("static", filename=verification_back, _external=True) if verification_back else ""
            )
            verification_selfie_url = (
                url_for("static", filename=verification_selfie, _external=True) if verification_selfie else ""
            )

            verification_result = verify_identity(
                provider=identity_provider,
                front_url=verification_front_url,
                back_url=verification_back_url,
                selfie_url=verification_selfie_url,
                document_number=document_number,
            )
            verification_status = verification_result.get("status", "pending")
            profile_meta["identity_verification"] = verification_result
            technician_verification_status = verification_status
            technician_verification_reason = verification_result.get("reason", "")

            profile = TechnicianProfile(
                user_id=user.id,
                full_name=full_name,
                specialties=",".join(services_selected) if services_selected else specialty,
                localities=locality_text,
                bio=json.dumps(profile_meta, ensure_ascii=True),
                technician_type="independiente",
                work_photos=json.dumps(work_photos, ensure_ascii=True),
                verification_id_front=verification_front or "",
                verification_id_back=verification_back or "",
                verification_selfie=verification_selfie or "",
                verification_status=verification_status,
            )
            db.session.add(profile)

        db.session.commit()

        email_sent, email_status = send_welcome_email(email, full_name)

        register_msg = REGISTER_MESSAGES.get(account_type, REGISTER_MESSAGES.get(role, "Cuenta creada con exito."))

        if email_sent:
            flash(f"{register_msg} Te enviamos un correo de bienvenida.", "success")
        else:
            if email_status == "mail-disabled":
                flash(f"{register_msg} El correo esta desactivado en el servidor.", "info")
            elif email_status == "mail-missing-config":
                flash(f"{register_msg} Falta configurar SMTP para envio de correo.", "warning")
            else:
                flash(f"{register_msg} No fue posible enviar el correo por ahora.", "warning")

        if role == "tecnico":
            if technician_verification_status == "approved":
                flash("Identidad validada: aprobado.", "success")
            elif technician_verification_status == "rejected":
                flash("Identidad validada: rechazada. Revisa documentos y selfie.", "danger")
            else:
                detail = f" ({technician_verification_reason})" if technician_verification_reason else ""
                flash(f"Identidad en revision: pendiente{detail}.", "info")

            # Después del registro del técnico, ir al login
            return redirect(url_for("auth.login"))

        return redirect(url_for("auth.login"))

    selected_type = request.args.get("account_type", request.args.get("role", "cliente")).strip().lower()
    if selected_type not in {"cliente", "tecnico"}:
        selected_type = "cliente"

    # Pasar request.form (ImmutableMultiDict) para que el template pueda usar .getlist()
    resp = current_app.make_response(
        render_template("auth/register.html", type=selected_type, form=request.form)
    )
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    return resp


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute; 30 per hour", methods=["POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        login_as = request.form.get("login_as", "cliente").strip().lower()
        admin_login_code = request.form.get("admin_login_code", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash("Credenciales invalidas.", "danger")
            return redirect(url_for("auth.login"))

        if login_as not in {"cliente", "tecnico", "admin"}:
            login_as = "cliente"

        if user.role != login_as:
            if user.role == "tecnico" and login_as == "cliente":
                flash(
                    "Tu cuenta es de Tecnico, no de Cliente. "
                    "Selecciona la pestana \u2018Tecnico\u2019 e intenta de nuevo.",
                    "warning",
                )
                return redirect(url_for("auth.login", login_as="tecnico"))
            elif user.role == "cliente" and login_as == "tecnico":
                flash(
                    "Tu cuenta es de Cliente, no de Tecnico. "
                    "Selecciona la pestana \u2018Cliente\u2019 e intenta de nuevo.",
                    "warning",
                )
                return redirect(url_for("auth.login", login_as="cliente"))
            flash("No tienes permisos para entrar con ese tipo de cuenta.", "danger")
            return redirect(url_for("auth.login"))

        if login_as == "admin":
            valid_admin_access, admin_access_message = _validate_admin_security_code(
                submitted_code=admin_login_code,
                code_env_name="ADMIN_LOGIN_CODE",
                fallback_code=current_app.config.get("ADMIN_LOGIN_CODE", ""),
                session_prefix="admin_login_security",
                not_configured_message="No hay contrasena de seguridad de admin configurada.",
            )
            if not valid_admin_access:
                flash(admin_access_message, "danger")
                return redirect(url_for("auth.login", login_as="admin"))

        if not user.is_active:
            flash("Tu cuenta esta desactivada. Contacta soporte.", "warning")
            return redirect(url_for("auth.login"))

        if login_as != "admin" and not user.two_factor_enabled:
            return _finish_successful_login(user)

        return _start_otp_login_challenge(user, login_as)

    return render_template(
        "auth/login.html",
        social_login_enabled={
            "google": _social_login_enabled("google"),
            "microsoft": _social_login_enabled("microsoft"),
        },
    )


@auth_bp.route("/google")
def google_auth():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    client = oauth.create_client("google")
    if client is None:
        flash("Google OAuth no esta configurado todavia.", "warning")
        return redirect(url_for("auth.login"))

    nonce = secrets.token_urlsafe(24)
    session["oauth_google_nonce"] = nonce
    return client.authorize_redirect(
        _create_oauth_redirect_uri("GOOGLE_OAUTH_REDIRECT_URI", "auth.google_callback"),
        nonce=nonce,
        prompt="select_account",
    )


@auth_bp.route("/google/callback")
def google_callback():
    client = oauth.create_client("google")
    if client is None:
        flash("Google OAuth no esta configurado todavia.", "warning")
        return redirect(url_for("auth.login"))

    try:
        token = client.authorize_access_token()
        nonce = session.pop("oauth_google_nonce", None)
        identity = _build_social_identity("google", token, nonce)
        user, created = _find_or_create_social_user("google", identity)
        if created:
            session["oauth_just_created"] = True
        return _start_otp_login_challenge(user, user.role)
    except (OAuthError, ValueError) as exc:
        session.pop("oauth_google_nonce", None)
        flash(str(exc) or "No fue posible iniciar sesion con Google.", "danger")
        return redirect(url_for("auth.login"))


@auth_bp.route("/microsoft")
def microsoft_auth():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    client = oauth.create_client("microsoft")
    if client is None:
        flash("Microsoft OAuth no esta configurado todavia.", "warning")
        return redirect(url_for("auth.login"))

    nonce = secrets.token_urlsafe(24)
    session["oauth_microsoft_nonce"] = nonce
    return client.authorize_redirect(
        _create_oauth_redirect_uri("MICROSOFT_OAUTH_REDIRECT_URI", "auth.microsoft_callback"),
        nonce=nonce,
        prompt="select_account",
    )


@auth_bp.route("/microsoft/callback")
def microsoft_callback():
    client = oauth.create_client("microsoft")
    if client is None:
        flash("Microsoft OAuth no esta configurado todavia.", "warning")
        return redirect(url_for("auth.login"))

    try:
        token = client.authorize_access_token()
        nonce = session.pop("oauth_microsoft_nonce", None)
        identity = _build_social_identity("microsoft", token, nonce)
        user, created = _find_or_create_social_user("microsoft", identity)
        if created:
            session["oauth_just_created"] = True
        return _start_otp_login_challenge(user, user.role)
    except (OAuthError, ValueError) as exc:
        session.pop("oauth_microsoft_nonce", None)
        flash(str(exc) or "No fue posible iniciar sesion con Microsoft.", "danger")
        return redirect(url_for("auth.login"))


@auth_bp.route("/admin-access", methods=["GET", "POST"])
def admin_access():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        admin_login_code = request.form.get("admin_login_code", "").strip()

        user = User.query.filter_by(email=email, role="admin").first()
        if not user or not user.check_password(password):
            flash("Credenciales admin invalidas.", "danger")
            return redirect(url_for("auth.admin_access"))

        valid_admin_access, admin_access_message = _validate_admin_security_code(
            submitted_code=admin_login_code,
            code_env_name="ADMIN_LOGIN_CODE",
            fallback_code=current_app.config.get("ADMIN_LOGIN_CODE", ""),
            session_prefix="admin_login_security",
            not_configured_message="No hay contrasena de seguridad de admin configurada.",
        )
        if not valid_admin_access:
            flash(admin_access_message, "danger")
            return redirect(url_for("auth.admin_access"))

        if not user.is_active:
            flash("Tu cuenta admin esta desactivada. Contacta soporte.", "warning")
            return redirect(url_for("auth.admin_access"))

        return _start_otp_login_challenge(user, "admin")

    return render_template("auth/admin_access.html")


@auth_bp.route("/verify-otp", methods=["GET", "POST"])
@auth_bp.route("/verificar", methods=["GET", "POST"])
@limiter.limit("10 per minute", methods=["POST"])
def verify_otp():
    if current_user.is_authenticated and session.get("2fa_ok"):
        return redirect(url_for("main.dashboard"))

    pre_user_id = session.get("pre_2fa_user_id")
    if not pre_user_id:
        flash("Inicia sesion para continuar.", "warning")
        return redirect(url_for("auth.login"))

    user = User.query.get(pre_user_id)
    if not user:
        session.pop("pre_2fa_user_id", None)
        session.pop("pre_2fa_login_as", None)
        flash("Tu sesion de verificacion expiro. Inicia sesion de nuevo.", "warning")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        otp_code = re.sub(r"\D", "", request.form.get("otp_code", ""))
        if len(otp_code) != 6:
            flash("Ingresa un codigo valido de 6 digitos.", "warning")
            return redirect(url_for("auth.verify_otp"))

        ok, status = verify_otp_for_user(user.id, otp_code)
        if not ok:
            if status == "expired":
                flash("El codigo expiro. Solicita uno nuevo.", "warning")
            elif status == "max-attempts":
                session.pop("pre_2fa_user_id", None)
                session.pop("pre_2fa_login_as", None)
                session.pop("oauth_just_created", None)
                flash("Superaste los intentos permitidos. Inicia sesion de nuevo.", "danger")
                return redirect(url_for("auth.login"))
            else:
                flash("Codigo invalido. Verifica e intenta de nuevo.", "danger")
            return redirect(url_for("auth.verify_otp"))

        if session.pop("oauth_just_created", False):
            flash("Tu cuenta se creo exitosamente. Ya puedes continuar en HogarFix.", "success")

        return _finish_successful_login(user)

    active_otp = get_active_otp(user.id)
    otp_remaining_seconds = 0
    if active_otp and active_otp.expires_at:
        otp_remaining_seconds = max(0, int((active_otp.expires_at - datetime.utcnow()).total_seconds()))

    return render_template(
        "auth/verify_otp.html",
        masked_email=user.email,
        otp_remaining_seconds=otp_remaining_seconds,
    )


@auth_bp.route("/resend-otp", methods=["POST"])
@limiter.limit("3 per minute; 10 per hour")
def resend_otp():
    pre_user_id = session.get("pre_2fa_user_id")
    if not pre_user_id:
        flash("Inicia sesion para solicitar un nuevo codigo.", "warning")
        return redirect(url_for("auth.login"))

    user = User.query.get(pre_user_id)
    if not user:
        session.pop("pre_2fa_user_id", None)
        session.pop("pre_2fa_login_as", None)
        flash("Tu sesion de verificacion expiro. Inicia sesion de nuevo.", "warning")
        return redirect(url_for("auth.login"))

    _record, otp_code, status = resend_otp_for_user(user.id)
    if status == "cooldown":
        flash("Debes esperar al menos 60 segundos para reenviar el codigo.", "warning")
        return redirect(url_for("auth.verify_otp"))
    if status == "hour-limit":
        flash("Alcanzaste el maximo de reenvios por hora. Intenta mas tarde.", "danger")
        return redirect(url_for("auth.verify_otp"))
    if status == "no-otp":
        _record, otp_code = issue_otp_for_user(user.id, channel="email")

    email_sent, _email_status = _send_login_otp_email(user.email, otp_code)
    if not email_sent:
        current_app.logger.warning(
            "[OTP resend] Email delivery issue for user %s (%s) — status: %s",
            user.id, user.email, _email_status,
        )
    flash("Te enviamos un nuevo codigo de verificacion.", "info")

    return redirect(url_for("auth.verify_otp"))


@auth_bp.route("/logout")
@login_required
def logout():
    pre_user_id = session.get("pre_2fa_user_id")
    if pre_user_id:
        clear_otp_for_user(pre_user_id)

    active_session_token = session.get("active_session_token")
    if active_session_token:
        active_session = UserSession.query.filter_by(session_token=active_session_token, revoked_at=None).first()
        if active_session:
            active_session.revoked_at = datetime.utcnow()
            db.session.commit()

    logout_user()
    session.pop("user_id", None)
    session.pop("2fa_ok", None)
    session.pop("pre_2fa_user_id", None)
    session.pop("pre_2fa_login_as", None)
    session.pop("active_session_token", None)
    flash("Sesion cerrada.", "secondary")
    return redirect(url_for("main.home"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
@limiter.limit("5 per minute; 15 per hour", methods=["POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = User.query.filter_by(email=email).first()

        if user:
            serializer = _get_serializer()
            token = serializer.dumps({"user_id": user.id})
            reset_url = _build_public_url("auth.reset_password", token=token)
            display_name = user.email.split("@")[0]
            if user.role == "tecnico" and user.technician_profile and user.technician_profile.full_name:
                display_name = user.technician_profile.full_name
            send_password_reset_email(
                to_email=user.email,
                full_name=display_name,
                reset_url=reset_url,
            )

        flash("Si el correo existe, recibira instrucciones para recuperar acceso.", "info")
        return redirect(url_for("auth.forgot_password"))

    return render_template("auth/forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    serializer = _get_serializer()

    try:
        data = serializer.loads(token, max_age=3600)
    except SignatureExpired:
        flash("El enlace expiro. Solicita uno nuevo.", "warning")
        return redirect(url_for("auth.forgot_password"))
    except BadData:
        flash("Enlace invalido.", "danger")
        return redirect(url_for("auth.forgot_password"))

    user = User.query.get(data.get("user_id"))
    if not user:
        flash("No se encontro el usuario.", "danger")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not _is_strong_password(password):
            flash(
                "La contrasena debe tener minimo 8 caracteres, una mayuscula, una minuscula, un numero y un caracter especial.",
                "warning",
            )
            return redirect(url_for("auth.reset_password", token=token))

        if password != confirm_password:
            flash("Las contrasenas no coinciden.", "danger")
            return redirect(url_for("auth.reset_password", token=token))

        user.set_password(password)
        db.session.commit()
        flash("Contrasena actualizada. Inicia sesion.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html")
