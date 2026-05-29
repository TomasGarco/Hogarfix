import csv
import io
import re
from collections import defaultdict
from datetime import datetime, timedelta

from flask import Blueprint, Response, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func

from app.extensions import db
from app.models import Announcement, Booking, LoginLog, Review, TechnicianProfile, User
from app.utils import role_required


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def check_rating_suspensions():
    """Suspende automáticamente técnicos con calificación promedio < 2.0 en >= 5 reseñas."""
    try:
        profiles = TechnicianProfile.query.filter(
            TechnicianProfile.suspended_at.is_(None)
        ).all()
        for profile in profiles:
            reviews = (
                Review.query
                .filter_by(technician_id=profile.user_id)
                .all()
            )
            if len(reviews) < 5:
                continue
            avg = sum(r.rating for r in reviews) / len(reviews)
            if avg < 2.0:
                profile.suspended_at = datetime.utcnow()
                profile.suspension_reason = f"Calificación promedio baja ({avg:.1f}/5)"
                profile.suspension_type = "temporal"
        db.session.commit()
    except Exception:
        db.session.rollback()


@admin_bp.route("/dashboard")
@login_required
@role_required("admin")
def dashboard():
    # Chequeo automático de suspensiones por calificación
    check_rating_suspensions()

    users = User.query.order_by(User.created_at.desc()).all()
    clients = (
        User.query.filter_by(role="cliente")
        .order_by(User.created_at.desc())
        .all()
    )
    technicians = (
        User.query.filter_by(role="tecnico")
        .order_by(User.created_at.desc())
        .all()
    )
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_clients = [u for u in clients if u.created_at and u.created_at >= week_ago]
    old_clients = [u for u in clients if not u.created_at or u.created_at < week_ago]
    new_technicians = [u for u in technicians if u.created_at and u.created_at >= week_ago]
    old_technicians = [u for u in technicians if not u.created_at or u.created_at < week_ago]
    profiles = TechnicianProfile.query.order_by(TechnicianProfile.created_at.desc()).all()
    logs = LoginLog.query.order_by(LoginLog.login_at.desc()).limit(20).all()
    admin_name = current_user.email.split("@")[0].replace(".", " ").replace("_", " ").title()
    parts = [p for p in admin_name.split() if p]
    admin_initials = ((parts[0][0] if parts else "A") + (parts[1][0] if len(parts) > 1 else "")).upper()
    return render_template(
        "admin/dashboard.html",
        users=users,
        clients=clients,
        technicians=technicians,
        new_clients=new_clients,
        old_clients=old_clients,
        new_technicians=new_technicians,
        old_technicians=old_technicians,
        profiles=profiles,
        logs=logs,
        admin_name=admin_name,
        admin_initials=admin_initials,
    )


@admin_bp.route("/usuarios")
@login_required
@role_required("admin")
def users_list():
    role = request.args.get("role", "cliente").strip().lower()
    age = request.args.get("age", "new").strip().lower()

    if role not in {"cliente", "tecnico", "admin"}:
        role = "cliente"
    if age not in {"new", "old", "all"}:
        age = "new"

    q = User.query.filter_by(role=role).order_by(User.created_at.desc())
    users = q.all()
    if age in {"new", "old"}:
        week_ago = datetime.utcnow() - timedelta(days=7)
        if age == "new":
            users = [u for u in users if u.created_at and u.created_at >= week_ago]
        else:
            users = [u for u in users if not u.created_at or u.created_at < week_ago]

    return render_template("admin/users.html", users=users, selected_role=role, selected_age=age)


@admin_bp.route("/usuario/<int:user_id>/toggle-active", methods=["POST"])
@login_required
@role_required("admin")
def toggle_user_active(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("No puedes desactivar tu propia cuenta admin.", "warning")
        return redirect(url_for("admin.dashboard"))

    user.is_active = not bool(user.is_active)
    db.session.commit()
    flash("Estado del usuario actualizado.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/usuario/<int:user_id>/delete", methods=["POST"])
@login_required
@role_required("admin")
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("No puedes eliminar tu propia cuenta admin.", "warning")
        return redirect(url_for("admin.dashboard"))

    db.session.delete(user)
    db.session.commit()
    flash("Usuario eliminado correctamente.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/tecnico/<int:profile_id>/verificacion", methods=["POST"])
@login_required
@role_required("admin")
def update_verification(profile_id):
    profile = TechnicianProfile.query.get_or_404(profile_id)
    status = request.form.get("verification_status", "pending")

    if status not in {"pending", "basic_verified", "approved", "fully_verified", "rejected"}:
        flash("Estado invalido.", "danger")
        return redirect(url_for("admin.dashboard"))

    profile.verification_status = status
    # Al verificar por primera vez → arrancar trial de 30 días
    if status in ("basic_verified", "fully_verified") and profile.subscription_status == "none":
        profile.subscription_status = "trial"
        profile.subscription_expires_at = datetime.utcnow() + timedelta(days=30)
    db.session.commit()
    flash("Verificacion actualizada.", "success")
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/tecnico/<int:profile_id>/suscripcion", methods=["POST"])
@login_required
@role_required("admin")
def manage_subscription(profile_id):
    profile = TechnicianProfile.query.get_or_404(profile_id)
    action = request.form.get("action", "")
    days_map = {"30": 30, "90": 90, "365": 365}
    if action in days_map:
        base = max(profile.subscription_expires_at or datetime.utcnow(), datetime.utcnow())
        profile.subscription_expires_at = base + timedelta(days=days_map[action])
        profile.subscription_status = "active"
        flash(f"Suscripcion de {profile.full_name} extendida {action} dias.", "success")
    elif action == "expire":
        profile.subscription_status = "expired"
        profile.subscription_expires_at = datetime.utcnow() - timedelta(seconds=1)
        flash(f"Suscripcion de {profile.full_name} marcada como vencida.", "warning")
    elif action == "trial":
        profile.subscription_status = "trial"
        profile.subscription_expires_at = datetime.utcnow() + timedelta(days=30)
        flash(f"Trial de 30 dias iniciado para {profile.full_name}.", "info")
    db.session.commit()
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/tecnico/<int:profile_id>/suspension", methods=["POST"])
@login_required
@role_required("admin")
def toggle_suspension(profile_id):
    """Suspender o reactivar manualmente un técnico."""
    profile = TechnicianProfile.query.get_or_404(profile_id)
    accion = request.form.get("accion", "suspender")
    motivo = request.form.get("motivo", "Suspension manual por administrador").strip() or "Suspension manual"
    tipo = request.form.get("tipo", "temporal")  # 'temporal' | 'definitiva'

    if accion == "reactivar":
        profile.suspended_at = None
        profile.suspension_reason = None
        profile.suspension_type = None
        profile.user.is_active = True
        flash(f"Técnico {profile.full_name} reactivado.", "success")
    else:
        profile.suspended_at = datetime.utcnow()
        profile.suspension_reason = motivo
        profile.suspension_type = tipo
        if tipo == "definitiva":
            profile.user.is_active = False
        flash(f"Técnico {profile.full_name} suspendido ({tipo}).", "warning")

    db.session.commit()
    return redirect(url_for("admin.dashboard"))


@admin_bp.route("/perfil", methods=["GET", "POST"])
@login_required
@role_required("admin")
def admin_profile():
    if request.method == "POST":
        form_type = request.form.get("form_type", "datos")

        if form_type == "datos":
            full_name = " ".join((request.form.get("full_name", "")).strip().split()).title()
            phone_country = (request.form.get("phone_country", "+57") or "+57").strip()
            phone = re.sub(r"\D", "", request.form.get("phone", ""))
            locality = " ".join((request.form.get("locality", "")).strip().split()).title()

            if not full_name:
                flash("El nombre es obligatorio.", "warning")
                return redirect(url_for("admin.admin_profile"))

            current_user.full_name = full_name
            current_user.phone_country = phone_country
            current_user.phone = phone or None
            current_user.locality = locality or None
            db.session.commit()
            flash("Datos actualizados correctamente.", "success")

        elif form_type == "password":
            current_password = request.form.get("current_password", "")
            new_password = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")

            if not current_user.check_password(current_password):
                flash("La contraseña actual no es correcta.", "danger")
                return redirect(url_for("admin.admin_profile"))

            if len(new_password) < 8 or not re.search(r"[A-Z]", new_password) \
                    or not re.search(r"[a-z]", new_password) or not re.search(r"\d", new_password) \
                    or not re.search(r"[^A-Za-z0-9]", new_password):
                flash("La contraseña debe tener mínimo 8 caracteres, mayúscula, minúscula, número y símbolo.", "warning")
                return redirect(url_for("admin.admin_profile"))

            if new_password != confirm_password:
                flash("Las contraseñas no coinciden.", "warning")
                return redirect(url_for("admin.admin_profile"))

            current_user.set_password(new_password)
            db.session.commit()
            flash("Contraseña actualizada correctamente.", "success")

        return redirect(url_for("admin.admin_profile"))

    return render_template("admin/profile.html")


    """
    Revisa todos los técnicos y aplica suspensiones automáticas según calificación promedio.
    Llamar periódicamente (ej: desde un job diario o al cargar el dashboard admin).

    Reglas del contrato:
    - Promedio < 2.5 por 30 días  → suspensión temporal
    - Promedio < 2.0 por 60 días  → suspensión definitiva (cuenta desactivada)
    """
    now = datetime.utcnow()
    profiles = TechnicianProfile.query.all()
    cambios = 0

    for profile in profiles:
        # Calificación promedio de los últimos 60 días
        desde_60 = now - timedelta(days=60)
        desde_30 = now - timedelta(days=30)

        avg_60 = db.session.query(func.avg(Review.rating)).filter(
            Review.technician_id == profile.user_id,
            Review.created_at >= desde_60,
        ).scalar()

        avg_30 = db.session.query(func.avg(Review.rating)).filter(
            Review.technician_id == profile.user_id,
            Review.created_at >= desde_30,
        ).scalar()

        count_30 = db.session.query(func.count(Review.id)).filter(
            Review.technician_id == profile.user_id,
            Review.created_at >= desde_30,
        ).scalar() or 0

        # Necesita al menos 3 reseñas para aplicar suspensión
        if count_30 < 3:
            continue

        ya_suspendido = profile.suspended_at is not None

        # Suspensión definitiva: promedio < 2.0 en 60 días
        if avg_60 is not None and float(avg_60) < 2.0 and profile.suspension_type != "definitiva":
            profile.suspended_at = now
            profile.suspension_reason = f"Calificacion promedio {float(avg_60):.1f} durante 60 dias (minimo requerido: 2.0)"
            profile.suspension_type = "definitiva"
            profile.user.is_active = False
            cambios += 1

        # Suspensión temporal: promedio < 2.5 en 30 días
        elif avg_30 is not None and float(avg_30) < 2.5 and not ya_suspendido:
            profile.suspended_at = now
            profile.suspension_reason = f"Calificacion promedio {float(avg_30):.1f} durante 30 dias (minimo requerido: 2.5)"
            profile.suspension_type = "temporal"
            cambios += 1

        # Reactivar suspensión temporal si mejoró
        elif ya_suspendido and profile.suspension_type == "temporal":
            if avg_30 is not None and float(avg_30) >= 2.5:
                profile.suspended_at = None
                profile.suspension_reason = None
                profile.suspension_type = None
                profile.user.is_active = True
                cambios += 1

    if cambios:
        db.session.commit()
    return cambios


# ══════════════════════════════════════════════════════════════════════
# GESTIÓN DE ANUNCIOS PROMOCIONALES
# ══════════════════════════════════════════════════════════════════════

@admin_bp.route("/anuncios")
@login_required
@role_required("admin")
def announcements():
    all_ann = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return render_template("admin/announcements.html", announcements=all_ann)


@admin_bp.route("/anuncios/crear", methods=["POST"])
@login_required
@role_required("admin")
def create_announcement():
    titulo      = request.form.get("titulo", "").strip()
    mensaje     = request.form.get("mensaje", "").strip() or None
    imagen      = request.form.get("imagen", "").strip() or None
    boton_texto = request.form.get("boton_texto", "").strip() or None
    boton_link  = request.form.get("boton_link", "").strip() or None

    if not titulo:
        flash("El título es obligatorio.", "warning")
        return redirect(url_for("admin.announcements"))

    # Parsear fechas opcionales
    def _parse_dt(raw):
        try:
            return datetime.strptime(raw.strip(), "%Y-%m-%dT%H:%M") if raw and raw.strip() else None
        except ValueError:
            return None

    ann = Announcement(
        titulo      = titulo,
        mensaje     = mensaje,
        imagen      = imagen,
        boton_texto = boton_texto,
        boton_link  = boton_link,
        activo      = request.form.get("activo") == "on",
        fecha_inicio = _parse_dt(request.form.get("fecha_inicio", "")),
        fecha_fin    = _parse_dt(request.form.get("fecha_fin", "")),
    )
    db.session.add(ann)
    db.session.commit()
    flash(f"Anuncio «{titulo}» creado correctamente.", "success")
    return redirect(url_for("admin.announcements"))


@admin_bp.route("/anuncios/<int:ann_id>/toggle", methods=["POST"])
@login_required
@role_required("admin")
def toggle_announcement(ann_id):
    ann = Announcement.query.get_or_404(ann_id)
    ann.activo = not ann.activo
    db.session.commit()
    estado = "activado" if ann.activo else "desactivado"
    flash(f"Anuncio «{ann.titulo}» {estado}.", "success")
    return redirect(url_for("admin.announcements"))


@admin_bp.route("/anuncios/<int:ann_id>/editar", methods=["POST"])
@login_required
@role_required("admin")
def edit_announcement(ann_id):
    ann = Announcement.query.get_or_404(ann_id)
    ann.titulo      = request.form.get("titulo", ann.titulo).strip() or ann.titulo
    ann.mensaje     = request.form.get("mensaje", "").strip() or None
    ann.imagen      = request.form.get("imagen", "").strip() or None
    ann.boton_texto = request.form.get("boton_texto", "").strip() or None
    ann.boton_link  = request.form.get("boton_link", "").strip() or None
    ann.activo      = request.form.get("activo") == "on"

    def _parse_dt(raw):
        try:
            return datetime.strptime(raw.strip(), "%Y-%m-%dT%H:%M") if raw and raw.strip() else None
        except ValueError:
            return None

    ann.fecha_inicio = _parse_dt(request.form.get("fecha_inicio", ""))
    ann.fecha_fin    = _parse_dt(request.form.get("fecha_fin", ""))
    db.session.commit()
    flash(f"Anuncio «{ann.titulo}» actualizado.", "success")
    return redirect(url_for("admin.announcements"))


@admin_bp.route("/anuncios/<int:ann_id>/eliminar", methods=["POST"])
@login_required
@role_required("admin")
def delete_announcement(ann_id):
    ann = Announcement.query.get_or_404(ann_id)
    titulo = ann.titulo
    db.session.delete(ann)
    db.session.commit()
    flash(f"Anuncio «{titulo}» eliminado.", "warning")
    return redirect(url_for("admin.announcements"))


# ══════════════════════════════════════════════════════════════════════
# DETALLE / EDICIÓN DE USUARIO
# ══════════════════════════════════════════════════════════════════════

@admin_bp.route("/usuario/<int:user_id>", methods=["GET", "POST"])
@login_required
@role_required("admin")
def user_detail(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == "POST":
        full_name = " ".join((request.form.get("full_name", "")).strip().split()).title()
        email     = (request.form.get("email", "")).strip().lower()
        phone     = re.sub(r"\D", "", request.form.get("phone", ""))
        role      = request.form.get("role", user.role).strip()
        locality  = " ".join((request.form.get("locality", "")).strip().split()).title()

        if role not in {"admin", "tecnico", "cliente"}:
            role = user.role

        # No permitir que el admin se cambie su propio rol
        if user.id == current_user.id and role != "admin":
            flash("No puedes cambiar tu propio rol.", "warning")
            return redirect(url_for("admin.user_detail", user_id=user_id))

        if email and email != user.email:
            exists = User.query.filter_by(email=email).first()
            if exists and exists.id != user.id:
                flash("Ese correo ya está registrado.", "danger")
                return redirect(url_for("admin.user_detail", user_id=user_id))
            user.email = email

        user.full_name = full_name or user.full_name
        user.phone     = phone or None
        user.locality  = locality or None
        user.role      = role
        db.session.commit()
        flash("Usuario actualizado.", "success")
        return redirect(url_for("admin.user_detail", user_id=user_id))

    bookings = Booking.query.filter(
        (Booking.client_id == user.id) | (Booking.technician_id == user.id)
    ).order_by(Booking.created_at.desc()).limit(20).all()
    return render_template("admin/user_detail.html", user=user, bookings=bookings)


# ══════════════════════════════════════════════════════════════════════
# DETALLE TÉCNICO
# ══════════════════════════════════════════════════════════════════════

@admin_bp.route("/tecnico/<int:profile_id>")
@login_required
@role_required("admin")
def tech_detail(profile_id):
    profile  = TechnicianProfile.query.get_or_404(profile_id)
    reviews  = Review.query.filter_by(technician_id=profile.user_id).order_by(Review.created_at.desc()).all()
    bookings = Booking.query.filter_by(technician_id=profile.user_id).order_by(Booking.created_at.desc()).limit(30).all()
    avg_rating = None
    if reviews:
        avg_rating = round(sum(r.rating for r in reviews) / len(reviews), 1)
    bio = profile._bio
    return render_template("admin/tech_detail.html", profile=profile, reviews=reviews, bookings=bookings, avg_rating=avg_rating, bio=bio)


# ══════════════════════════════════════════════════════════════════════
# GESTIÓN DE RESERVAS
# ══════════════════════════════════════════════════════════════════════

@admin_bp.route("/reservas")
@login_required
@role_required("admin")
def reservas_list():
    status = request.args.get("status", "all").strip()
    valid_statuses = {"pendiente", "confirmado", "completado", "cancelado"}
    q = Booking.query.order_by(Booking.created_at.desc())
    if status in valid_statuses:
        q = q.filter_by(status=status)
    bookings = q.all()
    return render_template("admin/reservas.html", bookings=bookings, selected_status=status)


@admin_bp.route("/reserva/<int:booking_id>/cancelar", methods=["POST"])
@login_required
@role_required("admin")
def cancel_booking_admin(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    booking.status = "cancelado"
    db.session.commit()
    flash("Reserva cancelada.", "warning")
    return redirect(request.referrer or url_for("admin.reservas_list"))


# ══════════════════════════════════════════════════════════════════════
# GESTIÓN DE RESEÑAS
# ══════════════════════════════════════════════════════════════════════

@admin_bp.route("/resenas")
@login_required
@role_required("admin")
def resenas_list():
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return render_template("admin/resenas.html", reviews=reviews)


@admin_bp.route("/resena/<int:review_id>/eliminar", methods=["POST"])
@login_required
@role_required("admin")
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    db.session.delete(review)
    db.session.commit()
    flash("Reseña eliminada.", "warning")
    return redirect(url_for("admin.resenas_list"))


# ═══════════════════════════════════════════════════════════════════
# REPORTES Y EXPORTACIÓN
# ═══════════════════════════════════════════════════════════════════

@admin_bp.route("/reportes")
@login_required
@role_required("admin")
def reports():
    twelve_ago = datetime.utcnow() - timedelta(days=365)

    users_by_month = defaultdict(int)
    for u in User.query.filter(User.created_at >= twelve_ago).all():
        users_by_month[u.created_at.strftime("%Y-%m")] += 1

    bookings_by_month = defaultdict(int)
    for b in Booking.query.filter(Booking.created_at >= twelve_ago).all():
        bookings_by_month[b.created_at.strftime("%Y-%m")] += 1

    months = sorted(set(list(users_by_month.keys()) + list(bookings_by_month.keys())))

    bookings_by_status = {
        "pendiente": Booking.query.filter_by(status="pendiente").count(),
        "confirmado": Booking.query.filter_by(status="confirmado").count(),
        "completado": Booking.query.filter_by(status="completado").count(),
        "cancelado": Booking.query.filter_by(status="cancelado").count(),
    }

    total_users = User.query.count()
    total_techs = User.query.filter_by(role="tecnico").count()
    total_clients = User.query.filter_by(role="cliente").count()
    total_bookings = Booking.query.count()
    verified_techs = TechnicianProfile.query.filter(
        TechnicianProfile.verification_status.in_(["approved", "fully_verified"])
    ).count()
    pending_techs = TechnicianProfile.query.filter_by(verification_status="pending").count()

    return render_template(
        "admin/reports.html",
        months=months,
        users_by_month=users_by_month,
        bookings_by_month=bookings_by_month,
        bookings_by_status=bookings_by_status,
        total_users=total_users,
        total_techs=total_techs,
        total_clients=total_clients,
        total_bookings=total_bookings,
        verified_techs=verified_techs,
        pending_techs=pending_techs,
    )


@admin_bp.route("/reportes/exportar")
@login_required
@role_required("admin")
def export_report():
    bookings = Booking.query.order_by(Booking.created_at.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Fecha creacion", "Cliente", "Tecnico", "Servicio",
                     "Localidad", "Fecha servicio", "Estado", "Metodo pago"])
    for b in bookings:
        client_name = (b.client.full_name or b.client.email) if b.client else ""
        tech_name = ""
        if b.technician and b.technician.technician_profile:
            tech_name = b.technician.technician_profile.full_name
        elif b.technician:
            tech_name = b.technician.email
        writer.writerow([
            b.id,
            b.created_at.strftime("%Y-%m-%d %H:%M"),
            client_name,
            tech_name,
            b.service_type,
            b.locality,
            str(b.booking_date),
            b.status,
            b.payment_method,
        ])
    csv_bytes = output.getvalue().encode("utf-8-sig")  # BOM para compatibilidad Excel
    return Response(
        csv_bytes,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=reservas_hogarfix.csv"},
    )


# ═══════════════════════════════════════════════════════════════════
# GESTIÓN DE COMPROBANTES DE PAGO
# ═══════════════════════════════════════════════════════════════════

@admin_bp.route("/comprobantes")
@login_required
@role_required("admin")
def payment_proofs():
    bookings_with_proof = (
        Booking.query
        .filter(Booking.payment_proof.isnot(None))
        .order_by(Booking.updated_at.desc())
        .all()
    )
    cash_pending = (
        Booking.query
        .filter_by(payment_method="efectivo", status="completado")
        .filter(Booking.cash_confirmed_at.is_(None))
        .order_by(Booking.updated_at.desc())
        .all()
    )
    return render_template(
        "admin/comprobantes.html",
        bookings_with_proof=bookings_with_proof,
        cash_pending=cash_pending,
    )


@admin_bp.route("/comprobante/<int:booking_id>/verificar", methods=["POST"])
@login_required
@role_required("admin")
def verify_payment(booking_id):
    """El admin marca un comprobante de pago como verificado (confirma pago efectivo)."""
    booking = Booking.query.get_or_404(booking_id)
    if booking.payment_method == "efectivo" and not booking.cash_confirmed_at:
        booking.cash_confirmed_at = datetime.utcnow()
        db.session.commit()
        flash(f"Pago en efectivo de la reserva #{booking.id} confirmado.", "success")
    else:
        flash(f"Comprobante de reserva #{booking.id} marcado como verificado.", "success")
        db.session.commit()
    return redirect(url_for("admin.payment_proofs"))
