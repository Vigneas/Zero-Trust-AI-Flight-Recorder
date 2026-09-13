import pytest
import os
import json
from autonomous_lending_capture_hook.merkle import MerkleLog

def test_merkle_log_append_and_proof(tmp_path):
    log_file = tmp_path / "merkle_state.json"
    log = MerkleLog(str(log_file))
    
    hash1 = "a" * 64
    hash2 = "b" * 64
    hash3 = "c" * 64
    
    log.append(hash1)
    log.append(hash2)
    log.append(hash3)
    
    assert log.size == 3
    
    proof = log.get_inclusion_proof(1)  # proof for hash2
    assert isinstance(proof, list)
    # The proof should contain siblings to reconstruct root
    assert len(proof) > 0
    
    # Check persistence
    with open(log_file, "r") as f:
        data = json.load(f)
        assert len(data["leaves"]) == 3
        assert data["leaves"][1] == hash2
