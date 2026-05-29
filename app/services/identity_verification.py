from __future__ import annotations

from typing import Dict

import requests
from flask import current_app


def _mock_verification(front_url: str, back_url: str, selfie_url: str) -> Dict[str, str]:
    if front_url and back_url and selfie_url:
        return {"status": "approved", "provider": "mock", "reason": "mock-auto-approved"}
    return {"status": "rejected", "provider": "mock", "reason": "missing-assets"}


def _call_provider(endpoint: str, headers: Dict[str, str], payload: Dict[str, str]) -> Dict[str, str]:
    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=25)
        if 200 <= response.status_code < 300:
            data = response.json() if response.content else {}
            status = (data.get("status") or data.get("decision") or "pending").strip().lower()
            if status not in {"approved", "rejected", "pending"}:
                status = "pending"
            return {"status": status, "provider": payload.get("provider", "api"), "reason": "api-response"}
        return {"status": "pending", "provider": payload.get("provider", "api"), "reason": f"http-{response.status_code}"}
    except Exception as exc:
        current_app.logger.warning("Identity verification request failed: %s", exc)
        return {"status": "pending", "provider": payload.get("provider", "api"), "reason": "request-error"}


def verify_identity(provider: str, front_url: str, back_url: str, selfie_url: str, document_number: str) -> Dict[str, str]:
    chosen = (provider or "mock").strip().lower()

    if chosen == "mock":
        return _mock_verification(front_url, back_url, selfie_url)

    payload = {
        "provider": chosen,
        "document_front_url": front_url,
        "document_back_url": back_url,
        "selfie_url": selfie_url,
        "document_number": document_number,
    }

    if chosen == "onfido":
        endpoint = (current_app.config.get("ONFIDO_VERIFY_ENDPOINT") or "").strip()
        api_key = (current_app.config.get("ONFIDO_API_KEY") or "").strip()
        if not endpoint or not api_key:
            return {"status": "pending", "provider": "onfido", "reason": "onfido-not-configured"}
        headers = {"Authorization": f"Token token={api_key}", "Content-Type": "application/json"}
        return _call_provider(endpoint, headers, payload)

    if chosen == "veriff":
        endpoint = (current_app.config.get("VERIFF_VERIFY_ENDPOINT") or "").strip()
        api_key = (current_app.config.get("VERIFF_API_KEY") or "").strip()
        if not endpoint or not api_key:
            return {"status": "pending", "provider": "veriff", "reason": "veriff-not-configured"}
        headers = {"X-AUTH-CLIENT": api_key, "Content-Type": "application/json"}
        return _call_provider(endpoint, headers, payload)

    return {"status": "pending", "provider": chosen, "reason": "unknown-provider"}
