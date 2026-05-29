import json

from flask import Blueprint, current_app, jsonify, request
from flask_login import current_user, login_required

from app.extensions import db
from app.models import TechnicianProfile, User
from app.utils import send_welcome_email


api_bp = Blueprint("api", __name__, url_prefix="/api")


def _as_text(value):
    return (value or "").strip()


def _as_list(value):
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def _normalize_verification_status(raw_status):
    value = _as_text(raw_status).lower()
    mapping = {
        "approved": "approved",
        "accept": "approved",
        "accepted": "approved",
        "clear": "approved",
        "pass": "approved",
        "passed": "approved",
        "rejected": "rejected",
        "declined": "rejected",
        "failed": "rejected",
        "fail": "rejected",
        "deny": "rejected",
        "pending": "pending",
        "processing": "pending",
        "in_review": "pending",
        "review": "pending",
    }
    return mapping.get(value, "pending")


def _extract_status_from_webhook(provider, payload):
    if provider == "onfido":
        checks = payload.get("payload", {}).get("resource", {}) if isinstance(payload.get("payload"), dict) else {}
        return _normalize_verification_status(
            payload.get("status")
            or payload.get("decision")
            or checks.get("result")
            or checks.get("status")
        )

    if provider == "veriff":
        verification = payload.get("verification", {}) if isinstance(payload.get("verification"), dict) else {}
        return _normalize_verification_status(
            payload.get("status")
            or payload.get("decision")
            or verification.get("status")
            or verification.get("code")
        )

    return _normalize_verification_status(payload.get("status") or payload.get("decision"))


def _find_technician_profile_by_payload(payload):
    user_id = payload.get("user_id") or payload.get("userId")
    if user_id:
        profile = TechnicianProfile.query.filter_by(user_id=user_id).first()
        if profile:
            return profile

    email = _as_text(payload.get("email") or payload.get("applicant_email") or payload.get("user_email")).lower()
    if email:
        user = User.query.filter_by(email=email).first()
        if user:
            profile = TechnicianProfile.query.filter_by(user_id=user.id).first()
            if profile:
                return profile

    document_number = _as_text(
        payload.get("document_number")
        or payload.get("documentNumber")
        or payload.get("id_number")
    )
    if document_number:
        candidates = TechnicianProfile.query.filter(TechnicianProfile.bio.contains(document_number)).all()
        for profile in candidates:
            try:
                profile_meta = json.loads(profile.bio or "{}")
            except Exception:
                profile_meta = {}
            if _as_text(profile_meta.get("document_number")) == document_number:
                return profile

    return None


def _require_admin_json():
    if not current_user.is_authenticated:
        return jsonify({"ok": False, "error": "No autenticado"}), 401
    if getattr(current_user, "role", "") != "admin":
        return jsonify({"ok": False, "error": "No autorizado"}), 403
    return None


@api_bp.route("/technicians/register", methods=["POST"])
def register_technician():
    payload = request.get_json(silent=True) or {}

    required_fields = [
        "fullName",
        "email",
        "password",
        "phone",
        "documentType",
        "documentNumber",
        "documentFrontUrl",
        "documentBackUrl",
        "selfieUrl",
        "category",
        "services",
        "yearsExperience",
        "address",
        "neighborhood",
        "locality",
        "chargeType",
        "basePrice",
        "days",
        "startTime",
        "endTime",
        "signatureData",
    ]

    missing = []
    for key in required_fields:
        value = payload.get(key)
        if value is None:
            missing.append(key)
        elif isinstance(value, str) and not value.strip():
            missing.append(key)
        elif isinstance(value, list) and len(value) == 0:
            missing.append(key)

    if missing:
        return jsonify({"ok": False, "error": "Campos obligatorios faltantes", "missing": missing}), 400

    email = _as_text(payload.get("email")).lower()
    if User.query.filter_by(email=email).first():
        return jsonify({"ok": False, "error": "El correo ya esta registrado"}), 409

    user = User(
        email=email,
        role="tecnico",
        full_name=_as_text(payload.get("fullName")),
        phone=_as_text(payload.get("phone")),
        locality=_as_text(payload.get("locality")),
        barrio=_as_text(payload.get("neighborhood")),
        address=_as_text(payload.get("address")),
        phone_verified=bool(payload.get("phoneVerified", False)),
        accepted_terms=True,
    )
    user.set_password(_as_text(payload.get("password")))

    services = _as_list(payload.get("services"))
    days = _as_list(payload.get("days"))

    profile_notes = {
        "document_type": _as_text(payload.get("documentType")),
        "document_number": _as_text(payload.get("documentNumber")),
        "years_experience": _as_text(payload.get("yearsExperience")),
        "charge_type": _as_text(payload.get("chargeType")),
        "base_price": payload.get("basePrice"),
        "days": days,
        "start_time": _as_text(payload.get("startTime")),
        "end_time": _as_text(payload.get("endTime")),
        "signature_data": _as_text(payload.get("signatureData")),
        "certifications_url": _as_text(payload.get("certificationsUrl")),
        "identity_provider": _as_text(payload.get("identityProvider")) or "mock",
    }

    technician_profile = TechnicianProfile(
        full_name=_as_text(payload.get("fullName")),
        bio=json.dumps(profile_notes, ensure_ascii=True),
        specialties=",".join(services),
        localities=_as_text(payload.get("locality")),
        price_range=f"{_as_text(payload.get('chargeType'))}:{payload.get('basePrice')}",
        work_photos=json.dumps(_as_list(payload.get("portfolioUrls")), ensure_ascii=True),
        verification_id_front=_as_text(payload.get("documentFrontUrl")),
        verification_id_back=_as_text(payload.get("documentBackUrl")),
        verification_selfie=_as_text(payload.get("selfieUrl")),
        verification_status=_as_text(payload.get("identityStatus")) or "pending",
    )

    try:
        db.session.add(user)
        db.session.flush()

        technician_profile.user_id = user.id
        db.session.add(technician_profile)
        db.session.commit()

        send_welcome_email(user.email, user.full_name or "Tecnico")

        return jsonify(
            {
                "ok": True,
                "message": "Registro tecnico creado",
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "role": user.role,
                },
                "verification_status": technician_profile.verification_status,
            }
        ), 201
    except Exception as exc:
        db.session.rollback()
        return jsonify({"ok": False, "error": "No se pudo crear el registro", "detail": str(exc)}), 500


@api_bp.route("/identity/webhook/<provider>", methods=["POST"])
def identity_webhook(provider):
    provider_name = _as_text(provider).lower()
    if provider_name not in {"onfido", "veriff"}:
        return jsonify({"ok": False, "error": "Proveedor no soportado"}), 400

    payload = request.get_json(silent=True) or {}

    configured_token = (
        _as_text(current_app.config.get("ONFIDO_WEBHOOK_TOKEN"))
        if provider_name == "onfido"
        else _as_text(current_app.config.get("VERIFF_WEBHOOK_TOKEN"))
    )

    incoming_token = _as_text(request.headers.get("X-Webhook-Token") or request.args.get("token"))
    if configured_token and incoming_token != configured_token:
        return jsonify({"ok": False, "error": "Token invalido"}), 401

    profile = _find_technician_profile_by_payload(payload)
    if not profile:
        return jsonify({"ok": False, "error": "Tecnico no encontrado"}), 404

    new_status = _extract_status_from_webhook(provider_name, payload)

    try:
        meta = json.loads(profile.bio or "{}")
    except Exception:
        meta = {}

    meta["identity_verification"] = {
        "provider": provider_name,
        "status": new_status,
        "webhook": payload,
    }

    profile.verification_status = new_status
    profile.bio = json.dumps(meta, ensure_ascii=True)
    db.session.commit()

    return jsonify({
        "ok": True,
        "message": "Estado de verificacion actualizado",
        "provider": provider_name,
        "status": new_status,
        "technician_profile_id": profile.id,
        "user_id": profile.user_id,
    }), 200


@api_bp.route("/technicians/firma-contrato", methods=["POST"])
def firma_contrato():
    """Guarda la firma digital del contrato post-registro."""
    payload = request.get_json(silent=True) or {}
    email = _as_text(payload.get("email")).lower()
    signature_data = _as_text(payload.get("signatureData"))

    if not email or not signature_data:
        return jsonify({"ok": False, "error": "email y signatureData son requeridos"}), 400

    user = User.query.filter_by(email=email, role="tecnico").first()
    if not user or not user.technician_profile:
        return jsonify({"ok": False, "error": "Tecnico no encontrado"}), 404

    profile = user.technician_profile
    try:
        meta = json.loads(profile.bio or "{}")
    except Exception:
        meta = {}

    meta["contract_signature"] = signature_data
    meta["contract_accepted_at"] = __import__("datetime").datetime.utcnow().isoformat()
    profile.bio = json.dumps(meta, ensure_ascii=True)
    db.session.commit()

    return jsonify({"ok": True, "message": "Firma guardada correctamente"}), 200


@api_bp.route("/admin/technicians/verification-status", methods=["GET"])
@login_required
def admin_technician_verification_status():
    auth_error = _require_admin_json()
    if auth_error is not None:
        return auth_error

    user_id = request.args.get("user_id", type=int)

    query = (
        db.session.query(User.id, User.email, TechnicianProfile.verification_status, TechnicianProfile.created_at)
        .join(TechnicianProfile, TechnicianProfile.user_id == User.id)
        .filter(User.role == "tecnico")
        .order_by(User.id.desc())
    )

    if user_id:
        query = query.filter(User.id == user_id)

    rows = query.all()
    items = [
        {
            "user_id": row.id,
            "email": row.email,
            "verification_status": row.verification_status or "pending",
            "updated_at": row.created_at.isoformat() if row.created_at else None,
        }
        for row in rows
    ]

    return jsonify({"ok": True, "count": len(items), "items": items}), 200
