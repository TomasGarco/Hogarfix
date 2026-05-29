import json
from datetime import datetime, timedelta

from flask import Blueprint, Response, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func

from app.extensions import db
from app.models import Availability, Booking, Notification, Review, TechnicianProfile, UserSession
from app.utils import role_required, save_upload
from flask import session as flask_session


technician_bp = Blueprint("technician", __name__, url_prefix="/tecnico")


@technician_bp.route("/agenda-json")
@login_required
@role_required("tecnico")
def agenda_json():
    """Devuelve reservas y disponibilidad como eventos FullCalendar."""
    events = []

    # ── Reservas ──────────────────────────────────────────────────────────
    bookings = Booking.query.filter_by(technician_id=current_user.id).all()
    color_map = {
        "pendiente":  {"backgroundColor": "#fd7e14", "borderColor": "#e8650a"},
        "confirmado": {"backgroundColor": "#0d6efd", "borderColor": "#0a58ca"},
        "cancelado":  {"backgroundColor": "#adb5bd", "borderColor": "#868e96"},
    }
    for b in bookings:
        if not b.booking_date or not b.booking_time:
            continue
        start_dt = datetime.combine(b.booking_date, b.booking_time)
        end_dt = start_dt + timedelta(hours=1)
        colors = color_map.get(b.status, color_map["pendiente"])
        events.append({
            "id": f"booking-{b.id}",
            "title": f"{b.service_type} — {b.locality}",
            "start": start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "end":   end_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "backgroundColor": colors["backgroundColor"],
            "borderColor":     colors["borderColor"],
            "textColor":       "#fff",
            "extendedProps": {
                "status": b.status,
                "notes":  b.notes or "",
            },
        })

    # ── Disponibilidad (slots libres) ─────────────────────────────────────
    slots = Availability.query.filter_by(technician_id=current_user.id, is_booked=False).all()
    for s in slots:
        if not s.date or not s.start_time:
            continue
        start_dt = datetime.combine(s.date, s.start_time)
        end_dt   = datetime.combine(s.date, s.end_time) if s.end_time else start_dt + timedelta(hours=1)
        events.append({
            "id": f"slot-{s.id}",
            "title": "Disponible",
            "start": start_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "end":   end_dt.strftime("%Y-%m-%dT%H:%M:%S"),
            "backgroundColor": "#d1fae5",
            "borderColor":     "#059669",
            "textColor":       "#065f46",
            "display": "background",
        })

    return jsonify(events)


@technician_bp.route("/contrato/pdf")
@login_required
@role_required("tecnico")
def descargar_contrato():
    from app.services.contract_pdf import generar_contrato_pdf
    profile = TechnicianProfile.query.filter_by(user_id=current_user.id).first()
    pdf_bytes = generar_contrato_pdf(current_user, profile)
    nombre_archivo = f"contrato-hogarfix-{current_user.id}.pdf"
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={nombre_archivo}"},
    )


@technician_bp.route("/dashboard")
@login_required
@role_required("tecnico")
def dashboard():
    bookings = Booking.query.filter_by(technician_id=current_user.id).order_by(Booking.created_at.desc()).all()
    profile = TechnicianProfile.query.filter_by(user_id=current_user.id).first()
    tech_name = profile.full_name if profile and profile.full_name else current_user.email.split("@")[0]
    parts = [p for p in tech_name.replace(".", " ").replace("_", " ").split() if p]
    tech_initials = ((parts[0][0] if parts else "T") + (parts[1][0] if len(parts) > 1 else "")).upper()
    counters = {
        "pendiente": sum(1 for b in bookings if b.status == "pendiente"),
        "confirmado": sum(1 for b in bookings if b.status == "confirmado"),
        "cancelado": sum(1 for b in bookings if b.status == "cancelado"),
        "completado": sum(1 for b in bookings if b.status == "completado"),
    }

    # ── Estadísticas de competitividad ───────────────────────────────────
    my_reviews = Review.query.filter_by(technician_id=current_user.id).all()
    review_count = len(my_reviews)
    avg_rating = round(sum(r.rating for r in my_reviews) / review_count, 1) if review_count else 0.0

    tech_avgs = (
        db.session.query(Review.technician_id, func.avg(Review.rating).label("avg"))
        .group_by(Review.technician_id)
        .all()
    )
    ranking_position = 1 + sum(1 for tid, tavg in tech_avgs if tid != current_user.id and float(tavg) > avg_rating)
    total_techs = max(TechnicianProfile.query.filter_by(verification_status="approved").count(), 1)

    non_cancelled = counters["pendiente"] + counters["confirmado"] + counters["completado"]
    completion_rate = round((counters["confirmado"] + counters["completado"]) / non_cancelled * 100) if non_cancelled else 0

    return render_template(
        "technician/dashboard.html",
        bookings=bookings,
        counters=counters,
        tech_name=tech_name,
        tech_initials=tech_initials,
        profile=profile,
        avg_rating=avg_rating,
        review_count=review_count,
        ranking_position=ranking_position,
        total_techs=total_techs,
        completion_rate=completion_rate,
        my_reviews=my_reviews,
    )


@technician_bp.route("/notificaciones")
@login_required
@role_required("tecnico")
def notifications():
    notifs = (
        Notification.query.filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(50)
        .all()
    )
    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return render_template("technician/notifications.html",
        notifications=notifs,
        unread_count=unread_count,
    )


@technician_bp.route("/perfil", methods=["GET", "POST"])
@login_required
@role_required("tecnico")
def profile():
    profile = TechnicianProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        profile = TechnicianProfile(user_id=current_user.id, full_name=current_user.email.split("@")[0])

    if request.method == "POST":
        form_type = request.form.get("form_type", "profile")

        # ── Cambiar contraseña ────────────────────────────────────────────
        if form_type == "password":
            current_password = request.form.get("current_password", "")
            new_password     = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")
            import re as _re
            def _strong(p):
                return (len(p) >= 8 and _re.search(r"[A-Z]", p) and _re.search(r"[a-z]", p)
                        and _re.search(r"\d", p) and _re.search(r"[^A-Za-z0-9]", p))
            if not current_user.check_password(current_password):
                flash("La contraseña actual no es correcta.", "danger")
            elif not _strong(new_password):
                flash("La nueva contraseña debe tener mínimo 8 caracteres, mayúscula, minúscula, número y símbolo.", "warning")
            elif new_password != confirm_password:
                flash("La confirmación de contraseña no coincide.", "warning")
            else:
                current_user.set_password(new_password)
                db.session.commit()
                flash("Contraseña actualizada correctamente.", "success")
            return redirect(url_for("technician.profile"))

        # ── Preferencias de notificación ──────────────────────────────────
        if form_type == "settings":
            current_user.notifications_enabled    = request.form.get("notifications_enabled") == "on"
            current_user.marketing_notifications  = request.form.get("marketing_notifications") == "on"
            db.session.commit()
            flash("Configuración actualizada.", "success")
            return redirect(url_for("technician.profile"))

        specialties = request.form.getlist("specialties")
        localities = request.form.get("localities", "")

        profile.full_name = request.form.get("full_name", "").strip() or profile.full_name

        # Actualizar campos editables dentro del JSON de bio
        new_desc = request.form.get("bio_description", "").strip()
        existing_bio = {}
        if profile.bio:
            try:
                existing_bio = json.loads(profile.bio)
            except Exception:
                existing_bio = {}
        existing_bio["service_description"] = new_desc
        existing_bio["document_type"] = request.form.get("bio_document_type", existing_bio.get("document_type", "")).strip()
        # Solo actualizar el número de documento si el usuario envía un valor nuevo (no el enmascarado)
        new_doc = request.form.get("bio_document_number", "").strip()
        if new_doc and not all(c in "*" for c in new_doc.replace(new_doc[-4:] if len(new_doc) > 4 else "", "")):
            existing_bio["document_number"] = new_doc
        existing_bio["charge_type"] = request.form.get("bio_charge_type", existing_bio.get("charge_type", "")).strip()
        existing_bio["base_price"] = request.form.get("bio_base_price", existing_bio.get("base_price", "")).strip()
        existing_bio["technician_address"] = request.form.get("bio_address", existing_bio.get("technician_address", "")).strip()
        existing_bio["years_experience"] = request.form.get("bio_years_experience", existing_bio.get("years_experience", "")).strip()
        days = [d.strip() for d in request.form.getlist("bio_availability_days") if d.strip()]
        if days:
            existing_bio["availability_days"] = days
        existing_bio["availability_start"] = request.form.get("bio_availability_start", existing_bio.get("availability_start", "")).strip()
        existing_bio["availability_end"] = request.form.get("bio_availability_end", existing_bio.get("availability_end", "")).strip()
        profile.bio = json.dumps(existing_bio, ensure_ascii=False)

        profile.specialties = ",".join(s.strip().lower() for s in specialties if s.strip())
        profile.localities = ",".join(
            l.strip().lower() for l in localities.split(",") if l.strip()
        )
        profile.price_range = request.form.get("price_range", "").strip()

        tech_type = request.form.get("technician_type", "independiente")
        if tech_type in {"independiente", "empresa_local", "ex_estado"}:
            profile.technician_type = tech_type

        p_photo = save_upload(request.files.get("profile_photo"), "profile")
        if p_photo:
            profile.profile_photo = p_photo

        existing_work = json.loads(profile.work_photos or "[]")
        for file in request.files.getlist("work_photos"):
            saved = save_upload(file, "work")
            if saved:
                existing_work.append(saved)
        profile.work_photos = json.dumps(existing_work)

        id_front = save_upload(request.files.get("verification_id_front"), "verification")
        id_back = save_upload(request.files.get("verification_id_back"), "verification")
        selfie = save_upload(request.files.get("verification_selfie"), "verification")

        if id_front:
            profile.verification_id_front = id_front
        if id_back:
            profile.verification_id_back = id_back
        if selfie:
            profile.verification_selfie = selfie

        if not profile.id:
            db.session.add(profile)

        db.session.commit()
        flash("Perfil actualizado.", "success")
        return redirect(url_for("technician.profile"))

    work_photos = json.loads(profile.work_photos or "[]") if profile.work_photos else []
    bio_meta = {}
    if profile.bio:
        try:
            bio_meta = json.loads(profile.bio)
        except Exception:
            bio_meta = {}
    # Enmascarar número de documento: mostrar solo últimos 4 dígitos
    raw_doc = bio_meta.get("document_number", "")
    masked_doc = ("*" * max(0, len(raw_doc) - 4) + raw_doc[-4:]) if len(raw_doc) > 4 else ("*" * len(raw_doc))

    notifications = (
        Notification.query.filter_by(user_id=current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(30)
        .all()
    )
    unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    active_sessions = (
        UserSession.query.filter_by(user_id=current_user.id, revoked_at=None)
        .order_by(UserSession.last_seen_at.desc())
        .limit(5)
        .all()
    )
    current_session_token = flask_session.get("active_session_token", "")

    return render_template(
        "technician/profile.html",
        profile=profile,
        work_photos=work_photos,
        bio_description=bio_meta.get("service_description", ""),
        bio_document_type=bio_meta.get("document_type", ""),
        bio_document_number=masked_doc,
        bio_charge_type=bio_meta.get("charge_type", ""),
        bio_base_price=bio_meta.get("base_price", ""),
        bio_availability_days=bio_meta.get("availability_days", []),
        bio_availability_start=bio_meta.get("availability_start", ""),
        bio_availability_end=bio_meta.get("availability_end", ""),
        bio_years_experience=bio_meta.get("years_experience", ""),
        bio_address=bio_meta.get("technician_address", ""),
        notifications=notifications,
        unread_count=unread_count,
        active_sessions=active_sessions,
        current_session_token=current_session_token,
    )


@technician_bp.route("/disponibilidad", methods=["GET", "POST"])
@login_required
@role_required("tecnico")
def availability():
    if request.method == "POST":
        date_raw = request.form.get("date", "")
        start_raw = request.form.get("start_time", "")
        end_raw = request.form.get("end_time", "")

        try:
            slot_date = datetime.strptime(date_raw, "%Y-%m-%d").date()
            start_time = datetime.strptime(start_raw, "%H:%M").time()
            end_time = datetime.strptime(end_raw, "%H:%M").time()
        except ValueError:
            flash("Fecha u hora invalida.", "danger")
            return redirect(url_for("technician.availability"))

        if start_time >= end_time:
            flash("La hora final debe ser mayor a la inicial.", "warning")
            return redirect(url_for("technician.availability"))

        slot = Availability(
            technician_id=current_user.id,
            date=slot_date,
            start_time=start_time,
            end_time=end_time,
        )
        db.session.add(slot)
        db.session.commit()
        flash("Horario agregado.", "success")
        return redirect(url_for("technician.availability"))

    slots = (
        Availability.query.filter_by(technician_id=current_user.id)
        .order_by(Availability.date.asc(), Availability.start_time.asc())
        .all()
    )
    from datetime import date as _date
    return render_template("technician/availability.html", slots=slots,
                           today_str=_date.today().isoformat())


@technician_bp.route("/disponibilidad/<int:slot_id>/eliminar", methods=["POST"])
@login_required
@role_required("tecnico")
def delete_availability(slot_id):
    slot = Availability.query.filter_by(id=slot_id, technician_id=current_user.id).first_or_404()
    if slot.is_booked:
        flash("No puedes eliminar un horario reservado.", "warning")
        return redirect(url_for("technician.availability"))

    db.session.delete(slot)
    db.session.commit()
    flash("Horario eliminado.", "secondary")
    return redirect(url_for("technician.availability"))


@technician_bp.route("/configuracion", methods=["GET", "POST"])
@login_required
@role_required("tecnico")
def tech_settings():
    import re as _re
    from datetime import datetime as _dt

    def _strong(p):
        return (len(p) >= 8 and _re.search(r"[A-Z]", p) and _re.search(r"[a-z]", p)
                and _re.search(r"\d", p) and _re.search(r"[^A-Za-z0-9]", p))

    if request.method == "POST":
        form_type = request.form.get("form_type", "").strip().lower()

        if form_type == "settings":
            current_user.notifications_enabled = request.form.get("notifications_enabled") == "on"
            current_user.marketing_notifications = request.form.get("marketing_notifications") == "on"
            db.session.commit()
            flash("Configuracion actualizada.", "success")
            return redirect(url_for("technician.tech_settings"))

        if form_type == "password":
            current_password = request.form.get("current_password", "")
            new_password = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")
            if not current_user.check_password(current_password):
                flash("La contrasena actual no es correcta.", "danger")
            elif not _strong(new_password):
                flash("La nueva contrasena debe tener minimo 8 caracteres, mayuscula, minuscula, numero y simbolo.", "warning")
            elif new_password != confirm_password:
                flash("La confirmacion de contrasena no coincide.", "warning")
            else:
                current_user.set_password(new_password)
                db.session.commit()
                flash("Contrasena actualizada correctamente.", "success")
            return redirect(url_for("technician.tech_settings"))

        if form_type == "2fa":
            current_user.two_factor_enabled = request.form.get("two_factor_enabled") == "on"
            db.session.commit()
            flash("Preferencia de verificacion en dos pasos actualizada.", "success")
            return redirect(url_for("technician.tech_settings"))

        if form_type == "close_sessions":
            current_token = flask_session.get("active_session_token")
            UserSession.query.filter(
                UserSession.user_id == current_user.id,
                UserSession.revoked_at.is_(None),
                UserSession.session_token != current_token,
            ).update({"revoked_at": _dt.utcnow()}, synchronize_session=False)
            db.session.commit()
            flash("Las otras sesiones activas fueron cerradas.", "success")
            return redirect(url_for("technician.tech_settings"))

        if form_type == "payment":
            allowed = {"efectivo", "nequi", "daviplata", "transferencia", "pse"}
            method = request.form.get("preferred_payment_method", "efectivo").strip().lower()
            if method not in allowed:
                method = "efectivo"
            current_user.preferred_payment_method = method
            db.session.commit()
            flash("Método de pago preferido actualizado.", "success")
            return redirect(url_for("technician.tech_settings"))

    active_sessions = (
        UserSession.query.filter_by(user_id=current_user.id, revoked_at=None)
        .order_by(UserSession.last_seen_at.desc())
        .all()
    )
    current_session_token = flask_session.get("active_session_token", "")
    return render_template(
        "technician/settings.html",
        active_sessions=active_sessions,
        current_session_token=current_session_token,
    )


# ── Planes de suscripción (diccionario centralizado) ──────────────────
SUBSCRIPTION_PLANS = {
    "basico": {
        "name": "Básico",
        "trial_days": 30,
        "icon": "bi-house-heart-fill",
        "color": "#6c757d",
        "accent": "#495057",
        "gradient": "linear-gradient(135deg,#f8f9fa 0%,#e9ecef 100%)",
        "border": "#ced4da",
        "badge_bg": "#e9ecef",
        "badge_color": "#495057",
        "badge": None,
        "popular": False,
        "free_forever": True,
        "price_label": "$0",
        "price_sub": "Siempre gratis",
        "price_future": None,
        "features": [
            "Hasta 10 reservas activas al mes",
            "Perfil visible en la plataforma",
            "Acceso a todas las localidades de Bogotá",
            "Notificaciones de nuevas reservas",
            "Soporte por correo electrónico",
        ],
        "limits": [
            "Sin badge de verificación",
            "Posición estándar en búsquedas",
            "Sin estadísticas de rendimiento",
            "Sin soporte prioritario",
        ],
        "groups": None,
    },
    "profesional": {
        "name": "Profesional",
        "trial_days": 0,
        "icon": "bi-stars",
        "color": "#0d6efd",
        "accent": "#0a58ca",
        "gradient": "linear-gradient(135deg,#eff6ff 0%,#dbeafe 100%)",
        "border": "#93c5fd",
        "badge_bg": "#dbeafe",
        "badge_color": "#1d4ed8",
        "badge": "PRO",
        "popular": True,
        "free_forever": False,
        "price_label": "$25.000",
        "price_sub": "/ mes",
        "price_future": None,
        "features": [
            "Reservas ilimitadas",
            "Badge PRO verificado",
            "Perfil destacado en búsquedas",
            "Todas las localidades",
            "Soporte prioritario",
            "Estadísticas de rendimiento",
        ],
        "limits": [],
        "groups": [
            {
                "title": "Reservas y clientes",
                "icon": "bi-calendar-check-fill",
                "color": "#0d6efd",
                "items": [
                    "Reservas ilimitadas al mes",
                    "Acepta y gestiona reservas en tiempo real",
                    "Recordatorios automáticos para tus clientes",
                    "Historial completo de servicios",
                ],
            },
            {
                "title": "Visibilidad y perfil",
                "icon": "bi-eye-fill",
                "color": "#0ea5e9",
                "items": [
                    "Badge PRO verificado en tu perfil",
                    "Apareces destacado en los resultados de búsqueda",
                    "Perfil con sello de técnico confiable",
                    "Apareces en la sección «Técnicos recomendados»",
                    "Todas las localidades de Bogotá desbloqueadas",
                ],
            },
            {
                "title": "Estadísticas y métricas",
                "icon": "bi-bar-chart-fill",
                "color": "#6366f1",
                "items": [
                    "Vistas de tu perfil por semana",
                    "Tasa de aceptación de reservas",
                    "Calificación promedio y evolución",
                    "Ingresos estimados del mes",
                ],
            },
            {
                "title": "Soporte",
                "icon": "bi-headset",
                "color": "#059669",
                "items": [
                    "Soporte prioritario por correo (respuesta en menos de 24h)",
                    "Acceso al centro de ayuda exclusivo para Pro",
                ],
            },
        ],
    },
    "elite": {
        "name": "Elite",
        "trial_days": 0,
        "icon": "bi-gem",
        "color": "#7c3aed",
        "accent": "#6d28d9",
        "gradient": "linear-gradient(135deg,#f5f3ff 0%,#ede9fe 100%)",
        "border": "#c4b5fd",
        "badge_bg": "#ede9fe",
        "badge_color": "#6d28d9",
        "badge": "ELITE",
        "popular": False,
        "free_forever": False,
        "price_label": "$55.000",
        "price_sub": "/ mes",
        "price_future": None,
        "features": [
            "Todo lo de Profesional",
            "Badge ELITE exclusivo",
            "Posición #1 en búsquedas locales",
            "Soporte prioritario 24/7",
            "Verificación acelerada",
            "Análisis avanzados de perfil",
            "Promoción en redes sociales",
        ],
        "limits": [],
        "groups": [
            {
                "title": "Todo lo de Profesional, más:",
                "icon": "bi-patch-check-fill",
                "color": "#7c3aed",
                "items": [
                    "Reservas ilimitadas",
                    "Badge PRO incluido",
                    "Perfil destacado en búsquedas",
                    "Historial y estadísticas completas",
                ],
            },
            {
                "title": "Máxima visibilidad",
                "icon": "bi-trophy-fill",
                "color": "#d97706",
                "items": [
                    "Badge ELITE exclusivo — diferénciate de todos",
                    "Posición #1 garantizada en búsquedas de tu localidad",
                    "Apareces primero en la sección «Técnicos recomendados»",
                    "Tarjeta de presentación digital personalizada",
                    "Promoción de tu perfil en redes sociales de HogarFix (Instagram · Facebook)",
                ],
            },
            {
                "title": "Analítica avanzada",
                "icon": "bi-graph-up-arrow",
                "color": "#6366f1",
                "items": [
                    "Tasa de conversión de visitas a reservas",
                    "Análisis de reputación y tendencias",
                    "Comparativa con técnicos de tu área",
                    "Reporte mensual de desempeño por correo",
                ],
            },
            {
                "title": "Soporte Elite 24/7",
                "icon": "bi-shield-fill-check",
                "color": "#059669",
                "items": [
                    "Soporte prioritario 24/7 por chat y correo",
                    "Verificación de identidad acelerada (menos de 24h)",
                    "Acceso anticipado a nuevas funciones de la plataforma",
                    "Asesor personal de cuenta asignado",
                ],
            },
        ],
    },
}


@technician_bp.route("/suscripcion/planes")
@login_required
@role_required("tecnico")
def subscription_plans():
    profile = TechnicianProfile.query.filter_by(user_id=current_user.id).first()
    return render_template(
        "technician/planes.html",
        profile=profile,
        plans=SUBSCRIPTION_PLANS,
    )


@technician_bp.route("/suscripcion")
@login_required
@role_required("tecnico")
def my_subscription():
    profile = TechnicianProfile.query.filter_by(user_id=current_user.id).first()
    plan_key = (profile.subscription_plan if profile and profile.subscription_plan else "basico")
    current_plan = SUBSCRIPTION_PLANS.get(plan_key, SUBSCRIPTION_PLANS["basico"])
    return render_template(
        "technician/suscripcion.html",
        profile=profile,
        plans=SUBSCRIPTION_PLANS,
        current_plan=current_plan,
        plan_key=plan_key,
    )


@technician_bp.route("/suscripcion/activar", methods=["POST"])
@login_required
@role_required("tecnico")
def activate_subscription():
    plan_key = request.form.get("plan", "basico").strip().lower()
    if plan_key not in SUBSCRIPTION_PLANS:
        flash("Plan no válido.", "danger")
        return redirect(url_for("technician.subscription_plans"))

    profile = TechnicianProfile.query.filter_by(user_id=current_user.id).first()
    if not profile:
        flash("Perfil no encontrado.", "danger")
        return redirect(url_for("technician.subscription_plans"))

    plan = SUBSCRIPTION_PLANS[plan_key]
    profile.subscription_plan = plan_key
    profile.subscription_status = "active"
    if plan.get("free_forever"):
        # Básico: gratis para siempre, sin vencimiento
        profile.subscription_expires_at = None
        msg = f"¡Plan {plan['name']} activado! Es gratuito para siempre."
    else:
        # Planes de pago: 1 año de acceso sandbox (sin cobro real aún)
        profile.subscription_expires_at = datetime.utcnow() + timedelta(days=365)
        msg = f"¡Plan {plan['name']} activado! (Modo sandbox — sin cobro durante la fase de prueba)."
    db.session.commit()

    flash(msg, "success")
    return redirect(url_for("technician.my_subscription"))


@technician_bp.route("/suscripcion/cancelar", methods=["POST"])
@login_required
@role_required("tecnico")
def cancel_subscription():
    profile = TechnicianProfile.query.filter_by(user_id=current_user.id).first()
    if not profile or profile.subscription_exempt:
        flash("No puedes cancelar esta suscripción.", "warning")
        return redirect(url_for("technician.my_subscription"))

    profile.subscription_status = "expired"
    profile.subscription_expires_at = datetime.utcnow()
    db.session.commit()

    flash("Tu suscripción ha sido cancelada.", "info")
    return redirect(url_for("technician.subscription_plans"))
