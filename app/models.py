from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db





class User(UserMixin, db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="cliente")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    phone_country = db.Column(db.String(10), nullable=True, default="+57")
    locality = db.Column(db.String(120), nullable=True)
    barrio = db.Column(db.String(120), nullable=True)
    address = db.Column(db.String(180), nullable=True)
    phone_verified = db.Column(db.Boolean, default=False, nullable=False)
    notifications_enabled = db.Column(db.Boolean, default=True, nullable=False)
    marketing_notifications = db.Column(db.Boolean, default=True, nullable=False)
    preferred_payment_method = db.Column(db.String(30), nullable=False, default='efectivo')
    two_factor_enabled = db.Column(db.Boolean, default=True, nullable=False)
    accepted_terms = db.Column(db.Boolean, default=False, nullable=False)
    accepted_terms_at = db.Column(db.DateTime, nullable=True)
    oauth_provider = db.Column(db.String(30), nullable=True, index=True)
    oauth_subject = db.Column(db.String(255), nullable=True, index=True)
    avatar_url = db.Column(db.String(255), nullable=True)

    # Relación uno a muchos con sesiones de usuario
    sessions = db.relationship('UserSession', back_populates='user', cascade='all, delete-orphan')

    # Relación uno a uno con TechnicianProfile
    technician_profile = db.relationship('TechnicianProfile', back_populates='user', uselist=False)

    # Relaciones para reservas (bookings)
    client_bookings = db.relationship('Booking', foreign_keys='Booking.client_id', back_populates='client')
    technician_bookings = db.relationship('Booking', foreign_keys='Booking.technician_id', back_populates='technician')

    # Relación uno a muchos con notificaciones
    notifications = db.relationship('Notification', back_populates='user', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class TechnicianProfile(db.Model):
    __tablename__ = "tecnicos"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), unique=True, nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    bio = db.Column(db.Text, default="")
    specialties = db.Column(db.String(255), default="")
    localities = db.Column(db.String(255), default="")
    price_range = db.Column(db.String(80), default="")
    technician_type = db.Column(db.String(30), nullable=False, default="independiente")
    profile_photo = db.Column(db.String(255), default="")
    work_photos = db.Column(db.Text, default="[]")
    verification_id_front = db.Column(db.String(255), default="")
    verification_id_back = db.Column(db.String(255), default="")
    verification_selfie = db.Column(db.String(255), default="")
    verification_status = db.Column(db.String(30), default="pending", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    suspended_at = db.Column(db.DateTime, nullable=True)
    suspension_reason = db.Column(db.String(255), nullable=True)
    suspension_type = db.Column(db.String(20), nullable=True)  # 'temporal' | 'definitiva'
    subscription_status = db.Column(db.String(20), nullable=False, default='none')  # none|trial|active|expired
    subscription_expires_at = db.Column(db.DateTime, nullable=True)
    subscription_plan = db.Column(db.String(20), nullable=False, default='mensual')
    subscription_exempt = db.Column(db.Boolean, nullable=False, default=False)

    user = db.relationship("User", back_populates="technician_profile")

    @property
    def subscription_active(self):
        if self.subscription_exempt:
            return True
        if self.subscription_status in ('trial', 'active'):
            if self.subscription_expires_at is None:
                return True
            return self.subscription_expires_at > datetime.utcnow()
        return False

    @property
    def subscription_days_left(self):
        if self.subscription_expires_at and self.subscription_status in ('trial', 'active'):
            delta = (self.subscription_expires_at - datetime.utcnow()).days
            return max(delta, 0)
        return 0

    @property
    def work_photos_list(self) -> list:
        import json as _json
        try:
            data = _json.loads(self.work_photos or "[]")
            return data if isinstance(data, list) else []
        except Exception:
            return []

    @property
    def _bio(self) -> dict:
        """Return parsed bio JSON dict; empty dict when unavailable or malformed."""
        import json as _json
        raw = (self.bio or "").strip()
        if raw.startswith("{"):
            try:
                data = _json.loads(raw)
                return data if isinstance(data, dict) else {}
            except (_json.JSONDecodeError, TypeError):
                pass
        return {}

    @property
    def service_description(self) -> str:
        return self._bio.get("service_description", "")

    @property
    def bio_base_price(self) -> str:
        val = self._bio.get("base_price", "")
        return str(val) if val else ""

    @property
    def bio_charge_type(self) -> str:
        return self._bio.get("charge_type", "")


class Booking(db.Model):
    __tablename__ = "reservas"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    technician_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    service_type = db.Column(db.String(80), nullable=False)
    locality = db.Column(db.String(120), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    booking_time = db.Column(db.Time, nullable=False)
    notes = db.Column(db.Text, default="")
    status = db.Column(db.String(20), default="pendiente", nullable=False)
    payment_method = db.Column(db.String(30), nullable=False, default="efectivo")
    payment_proof = db.Column(db.String(255), nullable=True)
    cash_confirmed_at = db.Column(db.DateTime, nullable=True)
    evidence_photos = db.Column(db.Text, default="[]")
    completion_note = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    @property
    def evidence_photos_list(self):
        import json as _j
        try:
            return _j.loads(self.evidence_photos or "[]") or []
        except Exception:
            return []

    client = db.relationship("User", foreign_keys=[client_id], back_populates="client_bookings")
    technician = db.relationship("User", foreign_keys=[technician_id], back_populates="technician_bookings")
    review = db.relationship("Review", back_populates="booking", uselist=False, cascade="all, delete-orphan")
    messages = db.relationship(
        "BookingMessage",
        foreign_keys="[BookingMessage.booking_id]",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="BookingMessage.created_at",
    )


class Availability(db.Model):
    __tablename__ = "disponibilidad"

    id = db.Column(db.Integer, primary_key=True)
    technician_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_booked = db.Column(db.Boolean, default=False, nullable=False)

    technician_user = db.relationship("User", foreign_keys=[technician_id])


class Review(db.Model):
    __tablename__ = "resenas"

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("reservas.id"), unique=True, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    technician_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    booking = db.relationship("Booking", back_populates="review")


class LoginLog(db.Model):
    __tablename__ = "logs_login"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    login_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ip_address = db.Column(db.String(80), default="")
    user_agent = db.Column(db.String(255), default="")


class OTPVerification(db.Model):
    __tablename__ = "otp_verifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False, index=True)
    code_hash = db.Column(db.String(64), nullable=False)
    salt = db.Column(db.String(64), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    attempts = db.Column(db.Integer, nullable=False, default=0)
    max_attempts = db.Column(db.Integer, nullable=False, default=5)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_sent_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    resend_count = db.Column(db.Integer, nullable=False, default=1)
    resend_window_start = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    delivery_channel = db.Column(db.String(20), nullable=False, default="email")


class Notification(db.Model):
    __tablename__ = "notificaciones"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False, index=True)
    type = db.Column(db.String(30), nullable=False, default="general")
    title = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    link_url = db.Column(db.String(255), nullable=True)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship("User", back_populates="notifications")


class UserSession(db.Model):
    __tablename__ = "user_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False, index=True)
    session_token = db.Column(db.String(64), nullable=False, unique=True)
    ip_address = db.Column(db.String(80), default="")
    user_agent = db.Column(db.String(255), default="")
    last_seen_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    revoked_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship("User", back_populates="sessions")


class PolicyAcceptance(db.Model):
    __tablename__ = "policy_acceptances"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False, index=True)
    policy_version = db.Column(db.String(10), nullable=False, default="1.0")
    accepted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ip_address = db.Column(db.String(80), nullable=True)

    user = db.relationship("User", backref=db.backref("policy_acceptances", lazy="dynamic"))


class Announcement(db.Model):
    """Anuncios y promociones que aparecen como modal al entrar a la app."""
    __tablename__ = "anuncios"

    id          = db.Column(db.Integer, primary_key=True)
    titulo      = db.Column(db.String(120), nullable=False)
    mensaje     = db.Column(db.Text, nullable=True)
    imagen      = db.Column(db.String(255), nullable=True)   # URL o ruta /static/…
    boton_texto = db.Column(db.String(60), nullable=True)
    boton_link  = db.Column(db.String(255), nullable=True)
    activo      = db.Column(db.Boolean, default=True, nullable=False)
    fecha_inicio = db.Column(db.DateTime, nullable=True)
    fecha_fin    = db.Column(db.DateTime, nullable=True)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @property
    def is_currently_active(self) -> bool:
        if not self.activo:
            return False
        now = datetime.utcnow()
        if self.fecha_inicio and self.fecha_inicio > now:
            return False
        if self.fecha_fin and self.fecha_fin < now:
            return False
        return True


class BookingMessage(db.Model):
    """Mensajes directos entre cliente y técnico dentro de una reserva."""
    __tablename__ = "booking_messages"

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("reservas.id", ondelete="CASCADE"), nullable=False, index=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)

    sender = db.relationship("User", foreign_keys=[sender_id])
