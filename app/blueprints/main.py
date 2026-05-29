from datetime import date, datetime
import json as _json
import re

from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required
from sqlalchemy import func

from app.extensions import db
from app.models import Availability, Booking, Notification, PolicyAcceptance, Review, TechnicianProfile, User, UserSession
from app.utils import create_notification, role_required, save_upload


main_bp = Blueprint("main", __name__)


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
    out = re.sub(
        r"(\d)([a-z])",
        lambda match: f"{match.group(1)}{match.group(2).upper()}",
        out,
        flags=re.IGNORECASE,
    )
    return re.sub(r"\s+", " ", out).strip()


def _normalize_person_name(value: str) -> str:
    text = re.sub(r"\s+", " ", (value or "").strip())
    if not text:
        return ""
    return " ".join(part.capitalize() for part in text.split(" "))


def _is_strong_password(password: str) -> bool:
    if len(password) < 8:
        return False
    has_upper = bool(re.search(r"[A-Z]", password))
    has_lower = bool(re.search(r"[a-z]", password))
    has_digit = bool(re.search(r"\d", password))
    has_special = bool(re.search(r"[^A-Za-z0-9]", password))
    return has_upper and has_lower and has_digit and has_special


def _build_booking_counters(bookings):
    return {
        "total": len(bookings),
        "pendiente": sum(1 for booking in bookings if booking.status == "pendiente"),
        "confirmado": sum(1 for booking in bookings if booking.status == "confirmado"),
        "cancelado": sum(1 for booking in bookings if booking.status == "cancelado"),
        "completado": sum(1 for booking in bookings if booking.status == "completado"),
    }


def _serialize_notification(notification: Notification):
    return {
        "id": notification.id,
        "type": notification.type,
        "title": notification.title,
        "message": notification.message,
        "link_url": notification.link_url or "",
        "is_read": notification.is_read,
        "created_at": notification.created_at.strftime("%Y-%m-%d %H:%M"),
    }


def _mask_phone(phone_country: str | None, phone: str | None) -> str:
    digits = (phone or "").strip()
    if not digits:
        return "Sin registrar"
    if len(digits) <= 4:
        return f"{phone_country or '+57'} {digits}"
    return f"{phone_country or '+57'} *** *** {digits[-4:]}"


@main_bp.route("/")
def home():
    technicians = (
        TechnicianProfile.query.join(User, User.id == TechnicianProfile.user_id)
        .filter(User.role == "tecnico")
        .order_by(TechnicianProfile.created_at.desc())
        .limit(6)
        .all()
    )
    return render_template("main/home.html", technicians=technicians)


@main_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == "cliente":
        return redirect(url_for("main.client_dashboard"))
    if current_user.role == "tecnico":
        return redirect(url_for("technician.dashboard"))
    if current_user.role == "admin":
        return redirect(url_for("admin.dashboard"))
    return redirect(url_for("main.home"))


@main_bp.route("/cliente/dashboard")
@login_required
@role_required("cliente")
def client_dashboard():
    bookings = Booking.query.filter_by(client_id=current_user.id).order_by(Booking.created_at.desc()).all()
    counters = _build_booking_counters(bookings)
    recent = bookings[:3]
    # Próxima cita activa (pendiente o confirmada, fecha futura)
    active_booking = (
        Booking.query
        .filter(
            Booking.client_id == current_user.id,
            Booking.status.in_(["pendiente", "confirmado"]),
            Booking.booking_date >= date.today(),
        )
        .order_by(Booking.booking_date.asc(), Booking.booking_time.asc())
        .first()
    )
    return render_template(
        "main/client_dashboard.html",
        bookings=bookings,
        recent=recent,
        counters=counters,
        active_booking=active_booking,
    )


@main_bp.route("/mi-cuenta", methods=["GET", "POST"])
@login_required
@role_required("cliente")
def account_profile():
    if request.method == "POST":
        form_type = request.form.get("form_type", "profile").strip().lower()

        if form_type == "profile":
            full_name = _normalize_person_name(request.form.get("full_name", ""))
            phone_country = (request.form.get("phone_country", "+57") or "+57").strip()
            phone = re.sub(r"\D", "", request.form.get("phone", ""))
            locality = _normalize_person_name(request.form.get("locality", ""))
            barrio = _normalize_person_name(request.form.get("barrio", ""))
            address = _normalize_address(request.form.get("address", ""))
            avatar_file = request.files.get("avatar_file")

            if phone and not (7 <= len(phone) <= 15):
                flash("El telefono debe tener entre 7 y 15 digitos.", "warning")
                return redirect(url_for("main.account_profile"))

            if not full_name:
                flash("Tu nombre es obligatorio para mostrar tu perfil.", "warning")
                return redirect(url_for("main.account_profile"))

            previous_phone = current_user.phone or ""
            saved_avatar = save_upload(avatar_file, "profile")

            current_user.full_name = full_name
            current_user.phone_country = phone_country or "+57"
            current_user.phone = phone
            current_user.locality = locality
            current_user.barrio = barrio
            current_user.address = address
            if phone != previous_phone:
                current_user.phone_verified = False
            if saved_avatar:
                current_user.avatar_url = saved_avatar
            db.session.commit()
            create_notification(
                current_user.id,
                "perfil",
                "Perfil actualizado",
                "Tus datos personales se guardaron correctamente.",
                url_for("main.account_profile", _anchor="perfil"),
            )
            flash("Tu perfil fue actualizado.", "success")
            return redirect(url_for("main.account_profile"))

        if form_type == "settings":
            current_user.notifications_enabled = request.form.get("notifications_enabled") == "on"
            current_user.marketing_notifications = request.form.get("marketing_notifications") == "on"
            db.session.commit()
            flash("Tu configuracion fue actualizada.", "success")
            return redirect(url_for("main.account_profile", _anchor="configuracion"))

        if form_type == "password":
            current_password = request.form.get("current_password", "")
            new_password = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")

            if not current_user.check_password(current_password):
                flash("La contrasena actual no es correcta.", "danger")
                return redirect(url_for("main.account_profile"))

            if not _is_strong_password(new_password):
                flash(
                    "La nueva contrasena debe tener minimo 8 caracteres, mayuscula, minuscula, numero y simbolo.",
                    "warning",
                )
                return redirect(url_for("main.account_profile"))

            if new_password != confirm_password:
                flash("La confirmacion de contrasena no coincide.", "warning")
                return redirect(url_for("main.account_profile"))

            current_user.set_password(new_password)
            db.session.commit()
            create_notification(
                current_user.id,
                "seguridad",
                "Contrasena actualizada",
                "Tu contrasena se cambio correctamente desde tu perfil.",
                url_for("main.account_profile", _anchor="seguridad"),
            )
            flash("Contrasena actualizada correctamente.", "success")
            return redirect(url_for("main.account_profile"))

    bookings = Booking.query.filter_by(client_id=current_user.id).order_by(Booking.created_at.desc()).all()
    counters = _build_booking_counters(bookings)
    recent_notifications = (
        Notification.query.filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(8)
        .all()
    )
    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    active_sessions = (
        UserSession.query.filter_by(user_id=current_user.id, revoked_at=None)
        .order_by(UserSession.last_seen_at.desc())
        .all()
    )
    current_session_token = session.get("active_session_token")
    service_history = bookings[:8]
    completed_reviews = (
        Review.query.filter_by(client_id=current_user.id).order_by(Review.created_at.desc()).limit(5).all()
    )
    return render_template(
        "main/profile.html",
        counters=counters,
        bookings=service_history,
        notifications=recent_notifications,
        unread_count=unread_count,
        active_sessions=active_sessions,
        current_session_token=current_session_token,
        completed_reviews=completed_reviews,
        masked_phone=_mask_phone(current_user.phone_country, current_user.phone),
    )


@main_bp.route("/mi-configuracion", methods=["GET", "POST"])
@login_required
@role_required("cliente")
def client_settings():
    if request.method == "POST":
        form_type = request.form.get("form_type", "").strip().lower()

        if form_type == "settings":
            current_user.notifications_enabled = request.form.get("notifications_enabled") == "on"
            current_user.marketing_notifications = request.form.get("marketing_notifications") == "on"
            db.session.commit()
            flash("Configuracion actualizada.", "success")
            return redirect(url_for("main.client_settings"))

        if form_type == "password":
            current_password = request.form.get("current_password", "")
            new_password = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")
            if not current_user.check_password(current_password):
                flash("La contrasena actual no es correcta.", "danger")
            elif not _is_strong_password(new_password):
                flash("La nueva contrasena debe tener minimo 8 caracteres, mayuscula, minuscula, numero y simbolo.", "warning")
            elif new_password != confirm_password:
                flash("La confirmacion de contrasena no coincide.", "warning")
            else:
                current_user.set_password(new_password)
                db.session.commit()
                flash("Contrasena actualizada correctamente.", "success")
            return redirect(url_for("main.client_settings"))

        if form_type == "2fa":
            current_user.two_factor_enabled = request.form.get("two_factor_enabled") == "on"
            db.session.commit()
            flash("Preferencia de verificacion en dos pasos actualizada.", "success")
            return redirect(url_for("main.client_settings"))

        if form_type == "close_sessions":
            current_token = session.get("active_session_token")
            UserSession.query.filter(
                UserSession.user_id == current_user.id,
                UserSession.revoked_at.is_(None),
                UserSession.session_token != current_token,
            ).update({"revoked_at": datetime.utcnow()}, synchronize_session=False)
            db.session.commit()
            flash("Las otras sesiones activas fueron cerradas.", "success")
            return redirect(url_for("main.client_settings"))

        if form_type == "payment":
            allowed = {"efectivo", "nequi", "daviplata", "transferencia", "pse"}
            method = request.form.get("preferred_payment_method", "efectivo").strip().lower()
            if method not in allowed:
                method = "efectivo"
            current_user.preferred_payment_method = method
            db.session.commit()
            flash("Método de pago preferido actualizado.", "success")
            return redirect(url_for("main.client_settings"))

    active_sessions = (
        UserSession.query.filter_by(user_id=current_user.id, revoked_at=None)
        .order_by(UserSession.last_seen_at.desc())
        .all()
    )
    current_session_token = session.get("active_session_token")
    return render_template(
        "main/settings.html",
        active_sessions=active_sessions,
        current_session_token=current_session_token,
    )


@main_bp.route("/mis-notificaciones")
@login_required
@role_required("cliente")
def notifications_page():
    notifications = (
        Notification.query.filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(50)
        .all()
    )
    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return render_template("main/notifications.html",
        notifications=notifications,
        unread_count=unread_count,
    )


@main_bp.route("/mi-cuenta/notificaciones")
@login_required
@role_required("cliente")
def account_notifications():
    notifications = (
        Notification.query.filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(12)
        .all()
    )
    return jsonify(
        {
            "items": [_serialize_notification(notification) for notification in notifications],
            "unread": Notification.query.filter_by(user_id=current_user.id, is_read=False).count(),
        }
    )


@main_bp.route("/mi-cuenta/notificaciones/<int:notification_id>/leer", methods=["POST"])
@login_required
@role_required("cliente", "tecnico")
def mark_notification_read(notification_id):
    notification = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first_or_404()
    notification.is_read = True
    db.session.commit()
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"ok": True})
    if current_user.role == "tecnico":
        return redirect(url_for("technician.notifications"))
    return redirect(url_for("main.notifications_page"))


@main_bp.route("/mi-cuenta/notificaciones/leer-todas", methods=["POST"])
@login_required
@role_required("cliente", "tecnico")
def mark_all_notifications_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({"is_read": True})
    db.session.commit()
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"ok": True})
    if current_user.role == "tecnico":
        return redirect(url_for("technician.notifications"))
    return redirect(url_for("main.notifications_page"))


@main_bp.route("/mi-cuenta/sesiones/cerrar-otras", methods=["POST"])
@login_required
@role_required("cliente", "tecnico")
def close_other_sessions():
    current_token = session.get("active_session_token")
    (
        UserSession.query.filter(
            UserSession.user_id == current_user.id,
            UserSession.revoked_at.is_(None),
            UserSession.session_token != current_token,
        ).update({"revoked_at": datetime.utcnow()}, synchronize_session=False)
    )
    db.session.commit()
    flash("Las otras sesiones activas fueron cerradas.", "success")
    if current_user.role == "tecnico":
        return redirect(url_for("technician.profile", _anchor="seguridad"))
    return redirect(url_for("main.account_profile", _anchor="seguridad"))


@main_bp.route("/mi-cuenta/seguridad/2fa", methods=["POST"])
@login_required
@role_required("cliente", "tecnico")
def toggle_two_factor():
    current_user.two_factor_enabled = request.form.get("two_factor_enabled") == "on"
    db.session.commit()
    flash("La preferencia de verificacion en dos pasos fue actualizada.", "success")
    if current_user.role == "tecnico":
        return redirect(url_for("technician.profile"))
    return redirect(url_for("main.account_profile", _anchor="seguridad"))


@main_bp.route("/mi-cuenta/repetir/<int:booking_id>")
@login_required
@role_required("cliente")
def repeat_service(booking_id):
    booking = Booking.query.filter_by(id=booking_id, client_id=current_user.id).first_or_404()
    return redirect(
        url_for(
            "booking.create_booking",
            technician_id=booking.technician_id,
            service_type=booking.service_type,
            locality=booking.locality,
            date=booking.booking_date.strftime("%Y-%m-%d"),
        )
    )


@main_bp.route("/terminos-y-condiciones")
def legal_terms():
    return render_template("main/legal_terms.html")


@main_bp.route("/politica-de-privacidad")
def legal_privacy():
    return render_template("main/legal_privacy.html")


@main_bp.route("/politica-de-cancelacion")
def legal_cancellation():
    return render_template("main/legal_cancellation.html")


POLICIES_VERSION = "1.0"
POLICIES_UPDATED = "2026-04-01"


@main_bp.route("/politicas")
def politicas():
    return render_template(
        "main/politicas.html",
        policies_version=POLICIES_VERSION,
        policies_updated=POLICIES_UPDATED,
    )


@main_bp.route("/api/policies")
def api_policies():
    return jsonify({
        "version": POLICIES_VERSION,
        "updated_at": POLICIES_UPDATED,
        "sections": ["privacidad", "terminos", "seguridad", "cookies"],
    })


@main_bp.route("/api/accept-policies", methods=["POST"])
@login_required
def api_accept_policies():
    version = (request.json or {}).get("version", POLICIES_VERSION) if request.is_json else request.form.get("version", POLICIES_VERSION)
    version = str(version).strip()[:10]
    ip = request.remote_addr or ""

    existing = PolicyAcceptance.query.filter_by(
        user_id=current_user.id, policy_version=version
    ).first()
    if not existing:
        record = PolicyAcceptance(
            user_id=current_user.id,
            policy_version=version,
            ip_address=ip,
        )
        db.session.add(record)
        db.session.commit()

    return jsonify({"ok": True, "version": version})


@main_bp.route("/buscar")
@login_required
@role_required("cliente")
def search_technicians():
    service = request.args.get("service", "").strip().lower()
    locality = request.args.get("locality", "").strip().lower()
    approx_date = request.args.get("approx_date", "").strip()
    price_min = request.args.get("price_min", "").strip()
    price_max = request.args.get("price_max", "").strip()
    min_rating_str = request.args.get("min_rating", "").strip()
    avail_day = request.args.get("avail_day", "").strip().lower()

    try:
        price_min_val = float(price_min) if price_min else None
    except ValueError:
        price_min_val = None
    try:
        price_max_val = float(price_max) if price_max else None
    except ValueError:
        price_max_val = None
    try:
        min_rating_val = float(min_rating_str) if min_rating_str else None
    except ValueError:
        min_rating_val = None

    tech_profiles = (
        TechnicianProfile.query.join(User, User.id == TechnicianProfile.user_id)
        .filter(User.role == "tecnico")
        .order_by(TechnicianProfile.created_at.desc())
        .all()
    )

    filtered = []
    available_map = {}

    parsed_date = None
    if approx_date:
        try:
            parsed_date = datetime.strptime(approx_date, "%Y-%m-%d").date()
        except ValueError:
            parsed_date = None

    for profile in tech_profiles:
        # Ocultar técnicos con suscripción vencida
        if not profile.subscription_active:
            continue

        specialties = [s.strip().lower() for s in (profile.specialties or "").split(",") if s.strip()]
        localities = [l.strip().lower() for l in (profile.localities or "").split(",") if l.strip()]

        if service and service not in specialties:
            continue
        if locality:
            if not any(locality in loc for loc in localities):
                continue

        # Filtro por precio base
        if price_min_val is not None or price_max_val is not None:
            raw_price = profile.bio_base_price
            if not raw_price:
                continue
            try:
                price_num = float("".join(c for c in str(raw_price) if c.isdigit()))
            except (ValueError, TypeError):
                continue
            if price_min_val is not None and price_num < price_min_val:
                continue
            if price_max_val is not None and price_num > price_max_val:
                continue

        # Filtro por día disponible (campo availability_days del bio JSON)
        if avail_day:
            bio = profile._bio
            days = bio.get("availability_days", [])
            if isinstance(days, str):
                days = [days]
            if not any(avail_day in d.lower() for d in days):
                continue

        if parsed_date:
            has_open_slot = (
                Availability.query.filter_by(
                    technician_id=profile.user_id,
                    date=parsed_date,
                    is_booked=False,
                ).first()
                is not None
            )
            if not has_open_slot:
                continue
            available_map[profile.user_id] = True

        filtered.append(profile)

    # Ordenar: Elite primero, luego Profesional, luego Básico
    _rank = {"elite": 0, "profesional": 1}
    filtered.sort(key=lambda pr: _rank.get(pr.subscription_plan if pr.subscription_active else "basico", 2))

    # Rating por técnico
    tech_ids = [pr.user_id for pr in filtered]
    rating_rows = (
        db.session.query(Review.technician_id, func.avg(Review.rating), func.count(Review.id))
        .filter(Review.technician_id.in_(tech_ids))
        .group_by(Review.technician_id)
        .all()
    ) if tech_ids else []
    rating_map = {row[0]: {"avg": round(row[1], 1), "count": row[2]} for row in rating_rows}

    # Filtro por calificación mínima (post-loop, una vez que tenemos rating_map)
    if min_rating_val is not None:
        filtered = [
            pr for pr in filtered
            if rating_map.get(pr.user_id, {}).get("avg", 0) >= min_rating_val
        ]

    filters = {
        "service": service,
        "locality": locality,
        "approx_date": approx_date,
        "price_min": price_min,
        "price_max": price_max,
        "min_rating": min_rating_str,
        "avail_day": avail_day,
    }
    return render_template(
        "main/search.html",
        technicians=filtered,
        filters=filters,
        available_map=available_map,
        rating_map=rating_map,
    )


@main_bp.route("/tecnico/<int:user_id>")
@login_required
def technician_public_profile(user_id):
    from flask import abort
    tech_user = User.query.filter_by(id=user_id, role="tecnico").first_or_404()
    profile = tech_user.technician_profile
    if not profile or not profile.subscription_active:
        abort(404)

    reviews = (
        Review.query.filter_by(technician_id=user_id)
        .order_by(Review.created_at.desc())
        .limit(10)
        .all()
    )
    avg_rating = round(sum(r.rating for r in reviews) / len(reviews), 1) if reviews else None

    work_photos = []
    try:
        work_photos = _json.loads(profile.work_photos or "[]") or []
    except Exception:
        pass

    return render_template(
        "main/tech_profile.html",
        profile=profile,
        tech_user=tech_user,
        reviews=reviews,
        avg_rating=avg_rating,
        review_count=len(reviews),
        work_photos=work_photos,
    )
