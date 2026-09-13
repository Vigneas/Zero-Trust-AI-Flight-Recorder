class PayloadExtractor:
    REQUIRED_FIELDS = ["identity", "data_classification", "policy_version", "model_version"]
    
    def extract(self, decision: dict) -> dict:
        extracted = {}
        for field in self.REQUIRED_FIELDS:
            if field not in decision:
                raise MissingFieldError(f"Missing required field: {field}")
            extracted[field] = decision[field]
            
        identity = extracted["identity"]
        # Basic heuristic for natural person identifier:
        # reject common system/service account prefixes or names
        invalid_keywords = ["api-key", "system", "service", "oauth-client", "bot"]
        if any(keyword in identity.lower() for keyword in invalid_keywords):
            raise InvalidIdentityError(f"Identity '{identity}' is not a valid natural person identifier.")
            
        return extracted

class MissingFieldError(Exception):
    pass

class InvalidIdentityError(Exception):
    pass
