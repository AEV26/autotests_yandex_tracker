from jsonschema import validate
import logging

logger = logging.getLogger(__name__)

def validate_response_schema(response, schema):
    try:
        validate(instance=response.json(), schema=schema)
    except Exception as e:
        logger.error(f"Schema validation failed: {e}")
        logger.error(f"Response: {response.text}")
        raise

def validate_error_response(response, schema):
    assert response.status_code >= 400, "Expected error response"
    validate_response_schema(response, schema)