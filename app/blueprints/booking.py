import json as _json
import os
from datetime import datetime

from flask import Blueprint, abort, current_app, flash, redirect, render_template, request, send_from_directory, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Availability, Booking, BookingMessage, Review, TechnicianProfile, User
from app.services.email import send_new_booking_to_technician
from app.utils import create_notification, role_required, save_upload


booking_bp = Blueprint("booking", __name__, url_prefix="/reservas")


@booking_bp.route("/crear/<int:technician_id>", methods=["GET", "POST"])
@login_required
@role_required("cliente")
def create_booking(technician_id):
    technician = User.query.filter_by(id=technician_id, role="tecnico").first_or_404()
    profile = TechnicianProfile.query.filter_by(user_id=technician.id).first()

    pref_date = request.args.get("date", "")
    pref_service = request.args.get("service_type", "").strip().lower()
    # Pre-fill locality: prefer URL param, then client's registered locality
    pref_locality = (
        request.args.get("locality", "").strip().lower()
        or (current_user.locality or "").strip().lower()
    )
    slots = []
    booked_count = 0
    total_slots = 0
    if pref_date:
        try:
            parsed = datetime.strptime(pref_date, "%Y-%m-%d").date()
            slots = Availability.query.filter_by(
                technician_id=technician_id, date=parsed, is_booked=False
            ).all()
            booked_count = Availability.query.filter_by(
                technician_id=technician_id, date=parsed, is_booked=True
            ).count()
            total_slots = len(slots) + booked_count
        except ValueError:
            pref_date = ""

    if request.method == "POST":
        service_type = request.form.get("service_type", "").strip().lower()
        locality = request.form.get("locality", "").strip().lower()
        notes = request.form.get("notes", "").strip()
        payment_method = request.form.get("payment_method", "efectivo").strip()

        date_raw = request.form.get("booking_date", "")
        time_raw = request.form.get("booking_time", "")

        try:
            booking_date = datetime.strptime(date_raw, "%Y-%m-%d").date()
            booking_time = datetime.strptime(time_raw, "%H:%M").time()
        except ValueError:
            flash("Fecha u hora invalida.", "danger")
            return redirect(url_for("booking.create_booking", technician_id=technician_id))

        slot = Availability.query.filter_by(
            technician_id=technician_id,
            date=booking_date,
            start_time=booking_time,
            is_booked=False,
        ).first()

        booking = Booking(
            client_id=current_user.id,
            technician_id=technician_id,
            service_type=service_type,
            locality=locality,
            booking_date=booking_date,
            booking_time=booking_time,
            notes=notes,
            payment_method=payment_method,
            status="pendiente",
        )
        # Mark slot as booked only if it exists (technician may not have pre-set slots)
        if slot:
            slot.is_booked = True

        db.session.add(booking)
        db.session.commit()

        # Notificacion interna al cliente
        create_notification(
            current_user.id,
            "booking_confirmed",
            "Reserva registrada",
            f"Tu solicitud de {service_type.title()} fue registrada para {booking_date} a las {booking_time.strftime('%H:%M')}.",
            url_for("main.account_profile", _anchor="historial"),
        )

        # Notificacion interna al tecnico
        create_notification(
            technician_id,
            "new_booking",
            "Nueva reserva recibida",
            f"{current_user.name} solicitó {service_type.title()} para el {booking_date} a las {booking_time.strftime('%H:%M')}.",
            url_for("technician.dashboard"),
        )

        # Email al tecnico
        try:
            send_new_booking_to_technician(technician, booking, current_user)
        except Exception as exc:
            current_app.logger.error("[booking] Error enviando email al tecnico %s: %s", technician.email, exc)

        flash("Reserva creada correctamente.", "success")
        return redirect(url_for("main.client_dashboard"))

    return render_template(
        "booking/create.html",
        technician=technician,
        profile=profile,
        pref_date=pref_date,
        pref_service=pref_service,
        pref_locality=pref_locality,
        slots=slots,
        booked_count=booked_count,
        total_slots=total_slots,
        now_date=datetime.today().strftime("%Y-%m-%d"),
    )


@booking_bp.route("/<int:booking_id>/estado", methods=["POST"])
@login_required
def update_booking_status(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    new_status = request.form.get("status", "").strip()

    if new_status not in {"pendiente", "confirmado", "cancelado", "completado"}:
        flash("Estado invalido.", "danger")
        return redirect(url_for("main.dashboard"))

    # Tecnico gestiona solicitudes; cliente solo puede cancelar su propia reserva.
    if current_user.role == "tecnico" and booking.technician_id == current_user.id:
        # ── Límite plan Básico: máx. 5 reservas activas ──────────────────────
        if new_status == "confirmado":
            _prof = TechnicianProfile.query.filter_by(user_id=current_user.id).first()
            _is_premium = (
                _prof
                and _prof.subscription_active
                and _prof.subscription_plan in ("profesional", "elite")
            )
            if not _is_premium:
                _active = Booking.query.filter(
                    Booking.technician_id == current_user.id,
                    Booking.status.in_(["pendiente", "confirmado"]),
                ).count()
                if _active >= 10:
                    return redirect(url_for("technician.dashboard", limit_reached=1))
        booking.status = new_status
    elif current_user.role == "cliente" and booking.client_id == current_user.id and new_status == "cancelado":
        booking.status = "cancelado"
    else:
        flash("No tienes permisos para esta accion.", "danger")
        return redirect(url_for("main.dashboard"))

    if booking.status == "cancelado":
        slot = Availability.query.filter_by(
            technician_id=booking.technician_id,
            date=booking.booking_date,
            start_time=booking.booking_time,
        ).first()
        if slot:
            slot.is_booked = False

    db.session.commit()

    if booking.client_id:
        status_messages = {
            "confirmado": ("booking_confirmed", "Reserva confirmada", "Tu tecnico confirmo la reserva."),
            "cancelado": ("booking_cancelled", "Reserva cancelada", "La reserva fue cancelada."),
            "pendiente": ("booking_pending", "Reserva pendiente", "La reserva sigue pendiente de confirmacion."),
            "completado": ("booking_completed", "Servicio completado", "Tu servicio fue completado. Ya puedes dejar tu reseña."),
        }
        notif_type, notif_title, notif_message = status_messages.get(
            booking.status,
            ("booking_update", "Reserva actualizada", "Tu reserva cambio de estado."),
        )
        create_notification(
            booking.client_id,
            notif_type,
            notif_title,
            notif_message,
            url_for("main.account_profile", _anchor="historial"),
        )

    flash("Estado de reserva actualizado.", "success")
    return redirect(url_for("main.dashboard"))


def _normalize_note(text: str) -> str:
    """Capitaliza primera letra y cada oración; colapsa espacios extra."""
    import re
    text = " ".join(text.split())   # colapsar espacios múltiples / saltos extra
    if not text:
        return text
    text = text[0].upper() + text[1:]   # primera letra en mayúscula
    # Mayúscula después de . ! ?
    text = re.sub(
        r'([.!?]\s+)([a-záéíóúüñ])',
        lambda m: m.group(1) + m.group(2).upper(),
        text,
    )
    return text


@booking_bp.route("/<int:booking_id>/completar", methods=["POST"])
@login_required
@role_required("tecnico")
def complete_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.technician_id != current_user.id:
        flash("No tienes permisos para esta accion.", "danger")
        return redirect(url_for("technician.dashboard"))
    if booking.status != "confirmado":
        flash("Solo se pueden completar reservas confirmadas.", "warning")
        return redirect(url_for("technician.dashboard"))

    photos = []
    for field in ("before_photos", "after_photos", "evidence_photos"):
        for f in request.files.getlist(field):
            saved = save_upload(f, "evidence")
            if saved:
                photos.append(saved)

    booking.evidence_photos = _json.dumps(photos)
    booking.completion_note = _normalize_note(request.form.get("completion_note", "").strip())
    booking.status = "completado"
    db.session.commit()

    create_notification(
        booking.client_id,
        "booking_completed",
        "Servicio completado",
        f"Tu servicio de {booking.service_type.title()} fue completado. Revisa las fotos de evidencia y deja tu reseña.",
        url_for("main.client_dashboard"),
    )

    flash("Servicio marcado como completado.", "success")
    return redirect(url_for("technician.dashboard"))


@booking_bp.route("/<int:booking_id>/resena", methods=["POST"])
@login_required
@role_required("cliente")
def create_review(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.client_id != current_user.id:
        flash("No puedes calificar esta reserva.", "danger")
        return redirect(url_for("main.client_dashboard"))

    if booking.status not in {"confirmado", "completado"}:
        flash("Solo puedes reseñar servicios confirmados o completados.", "warning")
        return redirect(url_for("main.client_dashboard"))

    if booking.review:
        flash("Ya enviaste una reseña.", "info")
        return redirect(url_for("main.client_dashboard"))

    try:
        rating = int(request.form.get("rating", "0"))
    except ValueError:
        rating = 0

    if rating < 1 or rating > 5:
        flash("La calificacion debe estar entre 1 y 5.", "danger")
        return redirect(url_for("main.client_dashboard"))

    review = Review(
        booking_id=booking.id,
        client_id=current_user.id,
        technician_id=booking.technician_id,
        rating=rating,
        comment=request.form.get("comment", "").strip(),
    )
    db.session.add(review)
    db.session.commit()

    create_notification(
        current_user.id,
        "review",
        "Calificacion enviada",
        "Tu opinion sobre el servicio fue guardada correctamente.",
        url_for("main.account_profile", _anchor="historial"),
    )

    flash("Gracias por tu reseña.", "success")
    return redirect(url_for("main.client_dashboard"))


@booking_bp.route("/<int:booking_id>/comprobante", methods=["POST"])
@login_required
@role_required("cliente")
def upload_payment_proof(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.client_id != current_user.id:
        abort(403)
    if booking.status not in ("confirmado", "completado"):
        flash("Solo puedes subir comprobante para reservas confirmadas o completadas.", "warning")
        return redirect(url_for("main.client_dashboard"))
    if booking.payment_method == "efectivo":
        flash("El pago en efectivo no requiere comprobante digital.", "info")
        return redirect(url_for("main.client_dashboard"))

    f = request.files.get("payment_proof")
    saved = save_upload(f, "payment")
    if not saved:
        flash("Selecciona una imagen válida (jpg, png, webp).", "warning")
        return redirect(url_for("main.client_dashboard"))

    booking.payment_proof = saved
    db.session.commit()

    create_notification(
        booking.technician_id,
        "payment_proof",
        "Comprobante de pago recibido",
        f"El cliente subió el comprobante de pago para la reserva de {booking.service_type.title()}.",
        url_for("technician.dashboard"),
    )

    flash("Comprobante guardado correctamente.", "success")
    return redirect(url_for("main.client_dashboard"))


@booking_bp.route("/<int:booking_id>/comprobante/ver")
@login_required
def view_payment_proof(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    u = current_user
    if not (u.id == booking.client_id or u.id == booking.technician_id or u.role == "admin"):
        abort(403)
    if not booking.payment_proof:
        abort(404)
    folder = os.path.join(current_app.root_path, "static", "uploads", "payment")
    filename = os.path.basename(booking.payment_proof)
    return send_from_directory(folder, filename)


@booking_bp.route("/<int:booking_id>/confirmar-efectivo", methods=["POST"])
@login_required
@role_required("tecnico")
def confirm_cash_payment(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.technician_id != current_user.id:
        abort(403)
    if booking.status != "completado" or booking.payment_method != "efectivo":
        flash("Solo puedes confirmar cobro en efectivo de servicios completados.", "warning")
        return redirect(url_for("technician.dashboard"))
    if booking.cash_confirmed_at:
        flash("El cobro en efectivo ya fue confirmado.", "info")
        return redirect(url_for("technician.dashboard"))

    booking.cash_confirmed_at = datetime.utcnow()
    db.session.commit()

    create_notification(
        booking.client_id,
        "cash_confirmed",
        "Cobro en efectivo confirmado",
        f"El técnico confirmó haber recibido el pago en efectivo por el servicio de {booking.service_type.title()}.",
        url_for("main.client_dashboard"),
    )

    flash("Cobro en efectivo confirmado correctamente.", "success")
    return redirect(url_for("technician.dashboard"))


@booking_bp.route("/<int:booking_id>/chat")
@login_required
def booking_chat(booking_id):
    """Chat directo entre cliente y técnico dentro de una reserva."""
    booking = Booking.query.get_or_404(booking_id)
    u = current_user
    if u.id not in (booking.client_id, booking.technician_id) and u.role != "admin":
        abort(403)
    messages = (
        BookingMessage.query
        .filter_by(booking_id=booking_id)
        .order_by(BookingMessage.created_at)
        .all()
    )
    base_tpl = "base_tech.html" if u.role == "tecnico" else "base_client.html"
    return render_template("booking/chat.html", booking=booking, messages=messages, base_tpl=base_tpl)
