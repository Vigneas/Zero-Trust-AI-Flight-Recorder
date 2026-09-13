import hashlib
import cbor2
from cryptography.hazmat.primitives.asymmetric import ed25519

class CryptoSealer:
    def __init__(self):
        # Generate a private key for testing/mocking
        self._ed25519_private_key = ed25519.Ed25519PrivateKey.generate()

    def canonicalize(self, payload: dict) -> bytes:
        """
        Produces deterministic RFC 8949 canonical CBOR.
        """
        # canonical=True ensures keys are sorted deterministically
        return cbor2.dumps(payload, canonical=True)

    def seal(self, canonical_bytes: bytes) -> tuple[str, bytes, bytes]:
        """
        Hashes the bytes and signs them with Ed25519 and a mock ML-DSA-65.
        Returns (sha256_hex, ed25519_signature, ml_dsa_65_signature).
        """
        hash_obj = hashlib.sha256(canonical_bytes)
        hash_hex = hash_obj.hexdigest()
        
        # We sign the raw bytes (or the hash, but usually the raw bytes)
        ed25519_sig = self._ed25519_private_key.sign(canonical_bytes)
        
        # Mock ML-DSA-65 signature (~3.3 KB of dummy data)
        # Using 3309 bytes as a representative size for ML-DSA-65
        ml_dsa_65_sig = b"MOCK_ML_DSA_65_" + b"0" * (3309 - 15)
        
        return hash_hex, ed25519_sig, ml_dsa_65_sig
