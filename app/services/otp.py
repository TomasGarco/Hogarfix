import hashlib
import hmac
import secrets
from datetime import datetime, timedelta

from flask import current_app

from app.extensions import db
from app.models import OTPVerification


def _otp_secret() -> str:
    return current_app.config.get("SECRET_KEY", "hogarfix-dev-secret")


def _now() -> datetime:
    return datetime.utcnow()


def _hash_code(code: str, salt: str) -> str:
    msg = f"{salt}:{code}".encode("utf-8")
    key = _otp_secret().encode("utf-8")
    return hmac.new(key, msg, hashlib.sha256).hexdigest()


def generate_otp_code() -> str:
    return f"{secrets.randbelow(1000000):06d}"


def issue_otp_for_user(user_id: int, channel: str = "email"):
    ttl_minutes = int(current_app.config.get("OTP_TTL_MINUTES", 3))
    max_attempts = int(current_app.config.get("OTP_MAX_ATTEMPTS", 3))

    OTPVerification.query.filter_by(user_id=user_id).delete()

    code = generate_otp_code()
    salt = secrets.token_hex(16)
    now = _now()
    record = OTPVerification(
        user_id=user_id,
        code_hash=_hash_code(code, salt),
        salt=salt,
        expires_at=now + timedelta(minutes=ttl_minutes),
        attempts=0,
        max_attempts=max_attempts,
        created_at=now,
        last_sent_at=now,
        resend_count=1,
        resend_window_start=now,
        delivery_channel=channel,
    )
    db.session.add(record)
    db.session.commit()
    return record, code


def get_active_otp(user_id: int):
    return OTPVerification.query.filter_by(user_id=user_id).first()


def can_resend_otp(record: OTPVerification):
    if not record:
        return False, "no-otp"

    now = _now()
    resend_seconds = int(current_app.config.get("OTP_RESEND_SECONDS", 60))
    if record.last_sent_at and (now - record.last_sent_at).total_seconds() < resend_seconds:
        return False, "cooldown"

    if not record.resend_window_start or (now - record.resend_window_start).total_seconds() >= 3600:
        record.resend_window_start = now
        record.resend_count = 0

    if record.resend_count >= 5:
        return False, "hour-limit"

    return True, "ok"


def resend_otp_for_user(user_id: int):
    record = get_active_otp(user_id)
    if not record:
        return None, None, "no-otp"

    ok, status = can_resend_otp(record)
    if not ok:
        return record, None, status

    code = generate_otp_code()
    now = _now()
    ttl_minutes = int(current_app.config.get("OTP_TTL_MINUTES", 3))

    record.salt = secrets.token_hex(16)
    record.code_hash = _hash_code(code, record.salt)
    record.expires_at = now + timedelta(minutes=ttl_minutes)
    record.attempts = 0
    record.last_sent_at = now
    record.resend_count = (record.resend_count or 0) + 1
    db.session.commit()

    return record, code, "ok"


def verify_otp_for_user(user_id: int, otp_code: str):
    record = get_active_otp(user_id)
    if not record:
        return False, "no-otp"

    now = _now()
    if record.expires_at <= now:
        db.session.delete(record)
        db.session.commit()
        return False, "expired"

    if record.attempts >= record.max_attempts:
        db.session.delete(record)
        db.session.commit()
        return False, "max-attempts"

    candidate_hash = _hash_code((otp_code or "").strip(), record.salt)
    if not hmac.compare_digest(candidate_hash, record.code_hash):
        record.attempts += 1
        if record.attempts >= record.max_attempts:
            db.session.delete(record)
        db.session.commit()
        return False, "invalid"

    db.session.delete(record)
    db.session.commit()
    return True, "ok"


def clear_otp_for_user(user_id: int):
    OTPVerification.query.filter_by(user_id=user_id).delete()
    db.session.commit()
