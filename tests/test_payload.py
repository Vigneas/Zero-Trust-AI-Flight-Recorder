import pytest
from autonomous_lending_capture_hook.payload import PayloadExtractor, MissingFieldError, InvalidIdentityError

def test_valid_payload_extraction():
    extractor = PayloadExtractor()
    decision = {
        "identity": "customer_9948",
        "data_classification": "financial",
        "policy_version": "v1.2",
        "model_version": "credit-alpha-3",
        "extra_stuff": "should be ignored"
    }
    extracted = extractor.extract(decision)
    assert extracted["identity"] == "customer_9948"
    assert extracted["data_classification"] == "financial"
    assert extracted["policy_version"] == "v1.2"
    assert extracted["model_version"] == "credit-alpha-3"
    assert "extra_stuff" not in extracted

def test_missing_field_raises_error():
    extractor = PayloadExtractor()
    decision = {
        "identity": "customer_9948",
        "data_classification": "financial",
        "policy_version": "v1.2"
        # missing model_version
    }
    with pytest.raises(MissingFieldError):
        extractor.extract(decision)

def test_invalid_identity_raises_error():
    extractor = PayloadExtractor()
    invalid_identities = [
        "api-key-1234",
        "system-service-account",
        "oauth-client-abc"
    ]
    for ident in invalid_identities:
        decision = {
            "identity": ident,
            "data_classification": "financial",
            "policy_version": "v1.2",
            "model_version": "credit-alpha-3"
        }
        with pytest.raises(InvalidIdentityError):
            extractor.extract(decision)
