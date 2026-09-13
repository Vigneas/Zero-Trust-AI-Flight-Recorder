import base64
import hashlib
from typing import Tuple, Union
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.exceptions import InvalidSignature

def recompute_sha256(cbor_payload_b64: str) -> Tuple[bytes, str]:
    """
    Decodes the base64-encoded CBOR payload and returns the raw canonical bytes
    and its recomputed SHA-256 hexadecimal digest.
    """
    raw_bytes = base64.b64decode(cbor_payload_b64)
    digest = hashlib.sha256(raw_bytes).hexdigest()
    return raw_bytes, digest

def verify_payload_hash(cbor_payload_b64: str, expected_hash: str) -> bool:
    """
    Verifies that sha256(decoded_cbor_bytes) matches the expected_hash.
    Guarantees bit-level integrity.
    """
    try:
        _, computed_hash = recompute_sha256(cbor_payload_b64)
        return computed_hash.lower() == expected_hash.strip().lower()
    except Exception:
        return False

def verify_ed25519_signature(
    raw_bytes: bytes,
    sig_b64: str,
    pub_key: Union[bytes, str]
) -> bool:
    """
    Verifies an Ed25519 classical digital signature against the provided public key.
    Public key can be raw 32 bytes, a base64-encoded string, or a hex-encoded string.
    """
    try:
        # 1. Parse public key bytes
        if isinstance(pub_key, str):
            pub_key_clean = pub_key.strip()
            # Check if hex (64 chars) or base64 (44 chars)
            if len(pub_key_clean) == 64:
                pk_bytes = bytes.fromhex(pub_key_clean)
            else:
                pk_bytes = base64.b64decode(pub_key_clean)
        else:
            pk_bytes = pub_key

        if len(pk_bytes) != 32:
            return False

        public_key_obj = ed25519.Ed25519PublicKey.from_public_bytes(pk_bytes)

        # 2. Decode signature bytes
        sig_bytes = base64.b64decode(sig_b64)
        if len(sig_bytes) != 64:
            return False

        # 3. Verify signature
        public_key_obj.verify(sig_bytes, raw_bytes)
        return True
    except (InvalidSignature, ValueError, Exception):
        return False

def verify_ml_dsa_65_signature(raw_bytes: bytes, sig_b64: str) -> Tuple[bool, str]:
    """
    Verifies the post-quantum ML-DSA-65 signature envelope.
    For hackathon scope, verifies the standardized 3309-byte length and mock prefix.
    """
    try:
        sig_bytes = base64.b64decode(sig_b64)
        if len(sig_bytes) != 3309:
            return False, f"Invalid ML-DSA-65 signature length: expected 3309 bytes, got {len(sig_bytes)}"

        if sig_bytes.startswith(b"MOCK_ML_DSA_65_"):
            return True, "SIMULATED_VALID: ML-DSA-65 post-quantum signature structure validated."
        
        return False, "Invalid ML-DSA-65 signature header."
    except Exception as exc:
        return False, f"Failed to parse ML-DSA-65 signature: {exc}"
