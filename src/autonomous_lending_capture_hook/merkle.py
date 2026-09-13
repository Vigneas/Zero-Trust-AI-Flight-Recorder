import json
import os
import hashlib

class MerkleLog:
    def __init__(self, filepath: str = "merkle_state.json"):
        self.filepath = filepath
        self.leaves = []
        self._load_state()
        
    def _load_state(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, "r") as f:
                data = json.load(f)
                self.leaves = data.get("leaves", [])
                
    def _save_state(self):
        with open(self.filepath, "w") as f:
            json.dump({"leaves": self.leaves}, f)
            
    def append(self, hash_hex: str):
        self.leaves.append(hash_hex)
        self._save_state()
        
    @property
    def size(self):
        return len(self.leaves)
        
    def get_inclusion_proof(self, leaf_index: int) -> list:
        """
        Generates a simplified RFC 6962 inclusion proof.
        For demonstration, returning a subset of the tree path.
        """
        if leaf_index < 0 or leaf_index >= self.size:
            raise ValueError("Index out of bounds")
            
        proof = []
        # Simplified proof logic for demonstration: 
        # normally we compute the tree and path, but here we just return the sibling if it exists
        if leaf_index % 2 == 0:
            if leaf_index + 1 < self.size:
                proof.append(self.leaves[leaf_index + 1])
        else:
            proof.append(self.leaves[leaf_index - 1])
            
        return proof
