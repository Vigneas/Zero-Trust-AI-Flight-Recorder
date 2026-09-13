import hashlib
from typing import List, Optional, Tuple

def verify_merkle_inclusion_proof(
    leaf_hash: str,
    proof: List[str],
    expected_root: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Recalculates the Merkle root from leaf_hash and an audit path of sibling hashes.
    If expected_root is specified, verifies that the calculated root matches.
    Returns (is_valid, calculated_root_hash).
    """
    current = leaf_hash.strip().lower()

    for sibling in proof:
        sibling_clean = sibling.strip().lower()
        # Combine hashes deterministically
        combined = (current + sibling_clean).encode("utf-8")
        current = hashlib.sha256(combined).hexdigest()

    if expected_root is not None:
        target = expected_root.strip().lower()
        is_match = (current == target)
        return is_match, current

    return True, current
