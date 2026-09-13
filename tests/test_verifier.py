import pytest
import base64
import json
import hashlib
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization

def test_crypto_verification_module():
    from verifier.crypto import (
        recompute_sha256,
        verify_payload_hash,
        verify_ed25519_signature,
        verify_ml_dsa_65_signature,
    )

    # 1. Payload and Hash check
    payload_bytes = b"sample_cbor_bytes_12345"
    payload_b64 = base64.b64encode(payload_bytes).decode("ascii")
    expected_hash = hashlib.sha256(payload_bytes).hexdigest()

    raw_bytes, computed_hash = recompute_sha256(payload_b64)
    assert raw_bytes == payload_bytes
    assert computed_hash == expected_hash
    assert verify_payload_hash(payload_b64, expected_hash) is True
    assert verify_payload_hash(payload_b64, "corrupted_hash_value") is False

    # 2. Ed25519 Signature Verification
    priv_key = ed25519.Ed25519PrivateKey.generate()
    pub_key = priv_key.public_key()
    pub_key_bytes = pub_key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    pub_key_b64 = base64.b64encode(pub_key_bytes).decode("ascii")

    sig = priv_key.sign(payload_bytes)
    sig_b64 = base64.b64encode(sig).decode("ascii")

    # Valid signature
    assert verify_ed25519_signature(payload_bytes, sig_b64, pub_key_b64) is True
    # Tampered payload
    assert verify_ed25519_signature(b"tampered_payload", sig_b64, pub_key_b64) is False
    # Tampered signature
    bad_sig_b64 = base64.b64encode(b"invalid_signature_length_64_bytes_00000000000000000000000000000000").decode("ascii")
    assert verify_ed25519_signature(payload_bytes, bad_sig_b64, pub_key_b64) is False

    # 3. Post-Quantum ML-DSA-65 signature
    valid_ml_sig = b"MOCK_ML_DSA_65_" + b"0" * (3309 - 15)
    valid_ml_b64 = base64.b64encode(valid_ml_sig).decode("ascii")
    is_valid, msg = verify_ml_dsa_65_signature(payload_bytes, valid_ml_b64)
    assert is_valid is True
    assert "SIMULATED_VALID" in msg

    bad_ml_b64 = base64.b64encode(b"corrupted_ml_sig").decode("ascii")
    bad_valid, _ = verify_ml_dsa_65_signature(payload_bytes, bad_ml_b64)
    assert bad_valid is False

def test_merkle_inclusion_proof_verification():
    from verifier.merkle import verify_merkle_inclusion_proof

    leaf_hash = "1111111111111111111111111111111111111111111111111111111111111111"
    sibling = "2222222222222222222222222222222222222222222222222222222222222222"
    expected_root = hashlib.sha256((leaf_hash + sibling).encode("utf-8")).hexdigest()

    # Success case with sibling proof
    ok, computed_root = verify_merkle_inclusion_proof(leaf_hash, [sibling], expected_root)
    assert ok is True
    assert computed_root == expected_root

    # Failure case with root mismatch
    ok_bad, _ = verify_merkle_inclusion_proof(leaf_hash, [sibling], "wrong_root_hash")
    assert ok_bad is False

def test_article_19_compliance_auditor():
    import cbor2
    from verifier.compliance import audit_article_19_payload

    # 1. Fully compliant Article 19 payload
    compliant_dict = {
        "identity": "citizen_99214_in",
        "data_classification": "PII_FINANCIAL_RECORDS",
        "policy_version": "POLICY-CREDIT-2026.1",
        "model_version": "MODEL-CREDIT-EVAL-v1.4",
        "decision": "APPROVED"
    }
    cbor_bytes = cbor2.dumps(compliant_dict, canonical=True)
    res = audit_article_19_payload(cbor_bytes)
    assert res["is_compliant"] is True
    assert res["natural_person_verified"] is True
    assert len(res["missing_fields"]) == 0

    # 2. Non-human / machine identity
    machine_dict = {
        "identity": "svc:automated_batch_caller",
        "data_classification": "PII_FINANCIAL_RECORDS",
        "policy_version": "POLICY-CREDIT-2026.1",
        "model_version": "MODEL-CREDIT-EVAL-v1.4"
    }
    res_mach = audit_article_19_payload(cbor2.dumps(machine_dict, canonical=True))
    assert res_mach["is_compliant"] is False
    assert res_mach["natural_person_verified"] is False

    # 3. Missing mandatory fields
    incomplete_dict = {
        "identity": "person_123",
        "model_version": "m1"
        # missing data_classification and policy_version
    }
    res_incomp = audit_article_19_payload(cbor2.dumps(incomplete_dict, canonical=True))
    assert res_incomp["is_compliant"] is False
    assert "data_classification" in res_incomp["missing_fields"]
    assert "policy_version" in res_incomp["missing_fields"]

def test_verifier_cli_e2e(tmp_path):
    import cbor2
    from verifier.cli import parse_receipt_file, verify_receipt

    priv_key = ed25519.Ed25519PrivateKey.generate()
    pub_key_bytes = priv_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
    pub_key_b64 = base64.b64encode(pub_key_bytes).decode("ascii")

    payload = {
        "identity": "person_98214",
        "data_classification": "PII_FINANCIAL_RECORDS",
        "policy_version": "v1.0",
        "model_version": "credit-v1",
        "status": "APPROVED"
    }
    raw_cbor = cbor2.dumps(payload, canonical=True)
    hash_hex = hashlib.sha256(raw_cbor).hexdigest()
    ed_sig = priv_key.sign(raw_cbor)
    ml_sig = b"MOCK_ML_DSA_65_" + b"0" * (3309 - 15)

    receipt_data = {
        "cbor_payload": base64.b64encode(raw_cbor).decode("ascii"),
        "sha256_hash": hash_hex,
        "ed25519_signature": base64.b64encode(ed_sig).decode("ascii"),
        "ml_dsa_65_signature": base64.b64encode(ml_sig).decode("ascii"),
        "merkle_inclusion_proof": [],
        "hardware_attestation": "SIMULATED",
        "witness_signatures": []
    }

    receipt_path = tmp_path / "receipt.json"
    with open(receipt_path, "w") as f:
        json.dump(receipt_data, f)

    parsed = parse_receipt_file(str(receipt_path))
    assert parsed["sha256_hash"] == hash_hex

    report = verify_receipt(parsed, public_key=pub_key_b64)
    assert report["overall_status"] == "VALID"
    assert report["checks"]["payload_integrity"]["passed"] is True
    assert report["checks"]["ed25519_signature"]["passed"] is True
    assert report["checks"]["article_19_compliance"]["passed"] is True
