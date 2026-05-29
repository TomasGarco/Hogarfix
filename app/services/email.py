from app.utils import send_email as _send_email


def send_email(email: str, subject: str, body: str, html_body: str | None = None):
    """Send email using the configured backend (plain text and optional HTML)."""
    return _send_email(subject=subject, to_email=email, text_body=body, html_body=html_body)


def send_new_booking_to_technician(technician, booking, client):
    """Notify the technician by email when a client creates a new booking."""
    service = booking.service_type.title()
    fecha = booking.booking_date.strftime("%d/%m/%Y")
    hora = booking.booking_time.strftime("%H:%M")
    localidad = (booking.locality or "No especificada").title()
    notas = booking.notes or "Sin notas adicionales."
    metodo = (booking.payment_method or "efectivo").title()
    phone_cliente = client.phone or "No registrado"

    text_body = (
        f"Hola {technician.name},\n\n"
        f"Tienes una nueva solicitud de reserva en HogarFix.\n\n"
        f"  Servicio:        {service}\n"
        f"  Fecha:           {fecha}\n"
        f"  Hora:            {hora}\n"
        f"  Localidad:       {localidad}\n"
        f"  Cliente:         {client.name}\n"
        f"  Tel. cliente:    {phone_cliente}\n"
        f"  Metodo de pago:  {metodo}\n"
        f"  Notas:           {notas}\n\n"
        f"Ingresa a tu panel para confirmar o rechazar la reserva:\n"
        f"http://localhost:5000/tecnico/\n\n"
        f"-- Equipo HogarFix"
    )

    html_body = f"""
    <div style="font-family:Arial,sans-serif;max-width:600px;margin:auto;border:1px solid #e5e7eb;border-radius:8px;overflow:hidden">
      <div style="background:#2563eb;padding:24px 32px">
        <h1 style="color:#fff;margin:0;font-size:22px">Nueva reserva recibida</h1>
        <p style="color:#bfdbfe;margin:4px 0 0">HogarFix &middot; Plataforma de servicios del hogar</p>
      </div>
      <div style="padding:32px">
        <p style="color:#374151;font-size:16px">Hola <strong>{technician.name}</strong>,</p>
        <p style="color:#374151">Un cliente ha solicitado tus servicios. Revisa los detalles y confirma o rechaza desde tu panel.</p>
        <table style="width:100%;border-collapse:collapse;margin:24px 0;font-size:15px">
          <tr style="background:#f9fafb"><td style="padding:10px 14px;color:#6b7280;font-weight:600;width:40%">Servicio</td><td style="padding:10px 14px;color:#111827">{service}</td></tr>
          <tr><td style="padding:10px 14px;color:#6b7280;font-weight:600">Fecha</td><td style="padding:10px 14px;color:#111827">{fecha}</td></tr>
          <tr style="background:#f9fafb"><td style="padding:10px 14px;color:#6b7280;font-weight:600">Hora</td><td style="padding:10px 14px;color:#111827">{hora}</td></tr>
          <tr><td style="padding:10px 14px;color:#6b7280;font-weight:600">Localidad</td><td style="padding:10px 14px;color:#111827">{localidad}</td></tr>
          <tr style="background:#f9fafb"><td style="padding:10px 14px;color:#6b7280;font-weight:600">Cliente</td><td style="padding:10px 14px;color:#111827">{client.name}</td></tr>
          <tr><td style="padding:10px 14px;color:#6b7280;font-weight:600">Tel. cliente</td><td style="padding:10px 14px;color:#111827">{phone_cliente}</td></tr>
          <tr style="background:#f9fafb"><td style="padding:10px 14px;color:#6b7280;font-weight:600">Metodo de pago</td><td style="padding:10px 14px;color:#111827">{metodo}</td></tr>
          <tr><td style="padding:10px 14px;color:#6b7280;font-weight:600">Notas</td><td style="padding:10px 14px;color:#111827">{notas}</td></tr>
        </table>
        <a href="http://localhost:5000/tecnico/" style="display:inline-block;background:#2563eb;color:#fff;padding:12px 28px;border-radius:6px;text-decoration:none;font-weight:600;font-size:15px">Ver reserva en mi panel</a>
        <p style="margin-top:32px;color:#9ca3af;font-size:13px">Este email fue enviado automaticamente por HogarFix.</p>
      </div>
    </div>
    """

    return _send_email(
        subject=f"[HogarFix] Nueva reserva: {service} el {fecha} a las {hora}",
        to_email=technician.email,
        text_body=text_body,
        html_body=html_body,
    )
