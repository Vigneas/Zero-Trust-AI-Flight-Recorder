from typing import Any, Dict, List
import cbor2

REJECTED_MACHINE_PREFIXES = (
    "svc:",
    "client:",
    "oauth:",
    "bot:",
    "system:",
    "service_account:",
)

MANDATORY_ARTICLE_19_FIELDS = (
    "identity",
    "data_classification",
    "policy_version",
    "model_version"
)

def audit_article_19_payload(raw_cbor_bytes: bytes) -> Dict[str, Any]:
    """
    Deserializes the canonical CBOR bytes and audits the payload for
    EU AI Act Article 19 mandatory context and natural person identity.
    """
    try:
        data = cbor2.loads(raw_cbor_bytes)
    except Exception as exc:
        return {
            "is_compliant": False,
            "natural_person_verified": False,
            "missing_fields": list(MANDATORY_ARTICLE_19_FIELDS),
            "extracted": {},
            "error": f"Failed to deserialize CBOR payload: {exc}"
        }

    if not isinstance(data, dict):
        return {
            "is_compliant": False,
            "natural_person_verified": False,
            "missing_fields": list(MANDATORY_ARTICLE_19_FIELDS),
            "extracted": {},
            "error": "Payload is not a valid map/dictionary."
        }

    missing_fields: List[str] = []
    for field in MANDATORY_ARTICLE_19_FIELDS:
        val = data.get(field)
        if val is None or (isinstance(val, str) and not val.strip()):
            missing_fields.append(field)

    # Validate natural person identity
    identity_val = str(data.get("identity", "")).strip().lower()
    natural_person_verified = True
    if not identity_val:
        natural_person_verified = False
    else:
        for prefix in REJECTED_MACHINE_PREFIXES:
            if identity_val.startswith(prefix):
                natural_person_verified = False
                break

    is_compliant = (len(missing_fields) == 0) and natural_person_verified

    return {
        "is_compliant": is_compliant,
        "natural_person_verified": natural_person_verified,
        "missing_fields": missing_fields,
        "extracted": {
            "identity": data.get("identity"),
            "data_classification": data.get("data_classification"),
            "policy_version": data.get("policy_version"),
            "model_version": data.get("model_version"),
            "decision_id": data.get("decision_id"),
            "status": data.get("status"),
            "risk_tier": data.get("risk_tier")
        }
    }
