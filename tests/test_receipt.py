import pytest
import json
import base64
from autonomous_lending_capture_hook.receipt import ReceiptBuilder

def test_receipt_generation(tmp_path):
    output_file = tmp_path / "receipt.json"
    builder = ReceiptBuilder(str(output_file))
    
    cbor_payload = b"\xa2\x61\x61\x01\x61\x62\x02"
    sha256_hash = "abc123hash"
    ed25519_sig = b"ed_sig_bytes"
    ml_dsa_65_sig = b"ml_sig_bytes"
    inclusion_proof = ["hash1", "hash2"]
    
    builder.build_and_save(
        cbor_payload,
        sha256_hash,
        ed25519_sig,
        ml_dsa_65_sig,
        inclusion_proof
    )
    
    assert output_file.exists()
    
    with open(output_file, "r") as f:
        data = json.load(f)
        
    assert data["hardware_attestation"] == "SIMULATED"
    assert data["witness_signatures"] == []
    assert data["sha256_hash"] == "abc123hash"
    assert data["merkle_inclusion_proof"] == ["hash1", "hash2"]
    
    # Verify base64 encoding
    assert base64.b64decode(data["cbor_payload"]) == cbor_payload
    assert base64.b64decode(data["ed25519_signature"]) == ed25519_sig
    assert base64.b64decode(data["ml_dsa_65_signature"]) == ml_dsa_65_sig
