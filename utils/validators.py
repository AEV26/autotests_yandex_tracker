import logging
import json
from pathlib import Path
from jsonschema import validate, ValidationError, SchemaError

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

class ResponseValidator:
    def __init__(self):
        self.schemas_dir = Path(__file__).parent.parent / "schemas"

    def validate_issue_response(self, response_json):
        schema = self._load_schema("issue_schema.json")
        validate(instance=response_json, schema=schema)

    def validate_error_response(self, response_json):
        schema = self._load_schema("error_schema.json")
        try:
            validate(instance=response_json, schema=schema)
        except ValidationError as e:
            raise ValidationError(f"{e.message}\nResponse was: {response_json}") from e

    def _load_schema(self, filename):
        with open(self.schemas_dir / filename) as f:
            return json.load(f)

    def validate_count_response(self, data):
        assert isinstance(data, (int, float))
        assert data >= 0

    def validate_search_response(self, data):
        assert isinstance(data, list)
        for item in data:
            assert isinstance(item, dict)
            assert "id" in item
            assert "key" in item
            assert "summary" in item
            assert "queue" in item
            assert "key" in item["queue"]

    def validate_move_response(self, data):
        assert isinstance(data, dict)
        assert "id" in data
        assert "key" in data
        assert "summary" in data
        assert "queue" in data
        assert "key" in data["queue"]

    def validate_changelog_response(self, data):
        schema = self._load_schema("changelog_schema.json")
        try:
            validate(instance=data, schema=schema)
        except ValidationError as e:
            raise AssertionError(f"Схема валидации не пройдена: {str(e)}")
        except SchemaError as e:
            raise AssertionError(f"Ошибка в схеме: {str(e)}")
        assert isinstance(data, list)
        assert len(data) > 0

    def validate_transitions_response(self, data):
        try:
            validate(instance=data, schema=self._load_schema("transitions_schema.json"))
        except ValidationError as e:
            raise AssertionError(f"Схема валидации переходов не пройдена: {str(e)}") from e
        except SchemaError as e:
            raise AssertionError(f"Ошибка в схеме переходов: {str(e)}") from e
        assert isinstance(data, list)
        assert len(data) > 0

    def validate_transition_result_response(self, data):
        try:
            validate(instance=data, schema=self._load_schema("transition_result_schema.json"))
        except ValidationError as e:
            raise AssertionError(f"Схема валидации результата перехода не пройдена: {str(e)}") from e
        except SchemaError as e:
            raise AssertionError(f"Ошибка в схеме результата перехода: {str(e)}") from e
        assert isinstance(data, dict)
        assert "self" in data
        assert "id" in data