import pytest
from autonomous_lending_capture_hook.crypto import CryptoSealer

def test_cbor_canonicalization():
    sealer = CryptoSealer()
    dict1 = {"a": 1, "b": 2, "c": 3}
    dict2 = {"c": 3, "a": 1, "b": 2}
    
    # Should produce same bytes due to deterministic serialization
    cbor1 = sealer.canonicalize(dict1)
    cbor2 = sealer.canonicalize(dict2)
    assert cbor1 == cbor2

def test_hash_and_hybrid_sealing():
    sealer = CryptoSealer()
    payload = {"identity": "customer_123", "data_classification": "PII"}
    canonical_bytes = sealer.canonicalize(payload)
    
    hash_hex, ed25519_sig, ml_dsa_65_sig = sealer.seal(canonical_bytes)
    
    assert isinstance(hash_hex, str)
    assert len(hash_hex) == 64  # SHA-256 hex string length
    
    assert isinstance(ed25519_sig, bytes)
    assert len(ed25519_sig) == 64  # Ed25519 signature is 64 bytes
    
    assert isinstance(ml_dsa_65_sig, bytes)
    # ML-DSA-65 mock signature should be a dummy string encoded to bytes
    assert ml_dsa_65_sig.startswith(b"MOCK_ML_DSA_65")
