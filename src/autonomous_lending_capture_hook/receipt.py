import json
import base64

class ReceiptBuilder:
    def __init__(self, output_path: str = "receipt.json"):
        self.output_path = output_path
        
    def build_and_save(
        self,
        cbor_payload: bytes,
        sha256_hash: str,
        ed25519_sig: bytes,
        ml_dsa_65_sig: bytes,
        inclusion_proof: list
    ):
        receipt = {
            "cbor_payload": base64.b64encode(cbor_payload).decode("utf-8"),
            "sha256_hash": sha256_hash,
            "ed25519_signature": base64.b64encode(ed25519_sig).decode("utf-8"),
            "ml_dsa_65_signature": base64.b64encode(ml_dsa_65_sig).decode("utf-8"),
            "merkle_inclusion_proof": inclusion_proof,
            "hardware_attestation": "SIMULATED",
            "witness_signatures": []
        }
        
        with open(self.output_path, "w") as f:
            json.dump(receipt, f, indent=2)
