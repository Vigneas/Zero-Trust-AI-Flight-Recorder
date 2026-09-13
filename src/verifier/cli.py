import argparse
import json
import os
import sys
from typing import Any, Dict, Optional

from verifier.crypto import (
    recompute_sha256,
    verify_payload_hash,
    verify_ed25519_signature,
    verify_ml_dsa_65_signature
)
from verifier.merkle import verify_merkle_inclusion_proof
from verifier.compliance import audit_article_19_payload

MANDATORY_RECEIPT_KEYS = (
    "cbor_payload",
    "sha256_hash",
    "ed25519_signature",
    "ml_dsa_65_signature",
    "merkle_inclusion_proof"
)

def parse_receipt_file(filepath: str) -> Dict[str, Any]:
    """
    Parses a receipt.json file and validates structural integrity.
    Executes 100% offline without network operations.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Receipt file not found: '{filepath}'")

    with open(filepath, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception as exc:
            raise ValueError(f"File is not valid JSON: {exc}")

    missing_keys = [k for k in MANDATORY_RECEIPT_KEYS if k not in data]
    if missing_keys:
        raise ValueError(f"Malformed receipt: missing mandatory fields {missing_keys}")

    return data

def verify_receipt(
    receipt: Dict[str, Any],
    public_key: Optional[str] = None,
    expected_root: Optional[str] = None
) -> Dict[str, Any]:
    """
    Orchestrates offline cryptographic verification stages and Article 19 audit inspection.
    """
    cbor_b64 = receipt["cbor_payload"]
    expected_hash = receipt["sha256_hash"]
    ed_sig_b64 = receipt["ed25519_signature"]
    ml_sig_b64 = receipt["ml_dsa_65_signature"]
    proof = receipt.get("merkle_inclusion_proof", [])

    raw_bytes, computed_hash = recompute_sha256(cbor_b64)

    # 1. Payload Integrity & Hash Check
    hash_passed = (computed_hash.lower() == expected_hash.strip().lower())

    # 2. Ed25519 Classical Signature Check
    if public_key:
        ed25519_passed = verify_ed25519_signature(raw_bytes, ed_sig_b64, public_key)
        ed_status = "PASSED" if ed25519_passed else "FAILED_INVALID_SIGNATURE"
    else:
        ed25519_passed = True
        ed_status = "SKIPPED_NO_PUBLIC_KEY"

    # 3. Post-Quantum ML-DSA-65 Check
    ml_passed, ml_status = verify_ml_dsa_65_signature(raw_bytes, ml_sig_b64)

    # 4. Merkle Inclusion Proof Check
    merkle_passed, merkle_root = verify_merkle_inclusion_proof(
        leaf_hash=expected_hash,
        proof=proof,
        expected_root=expected_root
    )

    # 5. Article 19 Regulatory Compliance Audit
    article_19_res = audit_article_19_payload(raw_bytes)
    article_19_passed = article_19_res["is_compliant"]

    overall_valid = all([
        hash_passed,
        ed25519_passed,
        ml_passed,
        merkle_passed,
        article_19_passed
    ])

    return {
        "overall_status": "VALID" if overall_valid else "INVALID",
        "sha256_hash": expected_hash,
        "calculated_merkle_root": merkle_root,
        "checks": {
            "payload_integrity": {
                "passed": hash_passed,
                "computed_hash": computed_hash,
                "expected_hash": expected_hash
            },
            "ed25519_signature": {
                "passed": ed25519_passed,
                "status": ed_status
            },
            "ml_dsa_65_signature": {
                "passed": ml_passed,
                "status": ml_status
            },
            "merkle_inclusion_proof": {
                "passed": merkle_passed,
                "proof_length": len(proof),
                "calculated_root": merkle_root,
                "expected_root": expected_root
            },
            "article_19_compliance": {
                "passed": article_19_passed,
                "details": article_19_res
            }
        }
    }

def print_human_report(report: Dict[str, Any]) -> None:
    print("=" * 68)
    print("      ZERO-TRUST AI FLIGHT RECORDER: OFFLINE VERIFIER REPORT      ")
    print("=" * 68)
    print(f"OVERALL STATUS: [{'PASS' if report['overall_status'] == 'VALID' else 'FAIL'}] {report['overall_status']}")
    print(f"Receipt Hash  : {report['sha256_hash']}")
    print(f"Merkle Root   : {report['calculated_merkle_root']}")
    print("-" * 68)
    print("CHECK SUMMARY:")

    chk = report["checks"]
    print(f"  [1] Canonical Payload SHA-256 : {'[PASS]' if chk['payload_integrity']['passed'] else '[FAIL]'}")
    print(f"  [2] Ed25519 Classical Sig     : {'[PASS]' if chk['ed25519_signature']['passed'] else '[FAIL]'} ({chk['ed25519_signature']['status']})")
    print(f"  [3] ML-DSA-65 Post-Quantum    : {'[PASS]' if chk['ml_dsa_65_signature']['passed'] else '[FAIL]'} ({chk['ml_dsa_65_signature']['status']})")
    print(f"  [4] Merkle Inclusion Proof    : {'[PASS]' if chk['merkle_inclusion_proof']['passed'] else '[FAIL]'}")
    print(f"  [5] EU AI Act Article 19 Audit: {'[PASS]' if chk['article_19_compliance']['passed'] else '[FAIL]'}")
    
    a19 = chk['article_19_compliance']['details']
    if a19.get("missing_fields"):
        print(f"      -> Missing Mandatory Fields: {a19['missing_fields']}")
    if not a19.get("natural_person_verified"):
        print("      -> Identity Violation: Identity failed natural person constraint.")
    print("=" * 68)

def main():
    parser = argparse.ArgumentParser(
        description="Zero-Trust AI Flight Recorder: Offline Cryptographic Auditor Verifier CLI."
    )
    parser.add_argument("--receipt", default="receipt.json", help="Path to receipt.json file (default: receipt.json)")
    parser.add_argument("--public-key", default=None, help="Bank's Ed25519 public key (hex or base64)")
    parser.add_argument("--root", default=None, help="Expected Merkle root hash (Signed Tree Head)")
    parser.add_argument("--json", action="store_true", help="Output machine-readable JSON report")

    args = parser.parse_args()

    try:
        receipt_data = parse_receipt_file(args.receipt)
    except Exception as exc:
        if args.json:
            print(json.dumps({"error": str(exc), "overall_status": "INVALID"}))
        else:
            print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    report = verify_receipt(
        receipt=receipt_data,
        public_key=args.public_key,
        expected_root=args.root
    )

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_human_report(report)

    if report["overall_status"] == "VALID":
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
