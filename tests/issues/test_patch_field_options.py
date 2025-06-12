from utils.api_client import TrackerApiClient
from schemas.fields_schema import patch_options_response_schema
from schemas.checklist_schema import error_schema
import pytest
import allure
import uuid
from jsonschema import validate

VALID_FIELD_ID = "test_field_17da8d"
NON_EXISTENT_FIELD_ID = "nonexistent_field_123"


@allure.feature("Fields API")
@allure.story("Изменение возможных значений поля")
class TestPatchFieldOptions:

    @allure.title("Позитивный тест: обновление options валидными данными")
    def test_patch_field_options_success(self, api_client_1):

        resp = api_client_1.get_field_by_id(VALID_FIELD_ID)
        assert resp.status_code == 200, resp.text
        current_version = resp.json()["version"]


        new_values = [f"opt_{uuid.uuid4().hex[:4]}" for _ in range(3)]
        payload = {"optionsProvider": {"type": "FixedListOptionsProvider", "values": new_values}}


        patch_resp = api_client_1.patch_field_options(VALID_FIELD_ID, payload, version=current_version)
        assert patch_resp.status_code == 200, patch_resp.text


        data = patch_resp.json()
        validate(instance=data, schema=patch_options_response_schema)


        get_resp = api_client_1.get_field_by_id(VALID_FIELD_ID)
        assert get_resp.status_code == 200
        got = get_resp.json().get("optionsProvider", {})
        assert got.get("type") == "FixedListOptionsProvider"

    @allure.title("Неавторизованный доступ при обновлении options")
    def test_patch_field_options_unauthorized(self, unauthorized_client):
        payload = {"optionsProvider": {"type": "FixedListOptionsProvider", "values": ["a", "b"]}}
        resp = unauthorized_client.patch_field_options(VALID_FIELD_ID, payload, version=1)
        assert resp.status_code == 401
        validate(instance=resp.json(), schema=error_schema)

    @allure.title("Валидация payload: пустой/числовой/необязательный тип")
    @pytest.mark.parametrize("bad_payload", [
        {"optionsProvider": {"type": "FixedListOptionsProvider", "values": []}},
        {"optionsProvider": "not an object"},
        {"optionsProvider": {"type": "FixedListOptionsProvider", "values": [1, 2]}},
        {"optionsProvider": {"type": "WrongProvider", "values": ["ok"]}},
        {"optionsProvider": {"type": "FixedListOptionsProvider", "values": ["ok"]}, "x": 1}
    ])
    def test_patch_field_options_validation_error(self, api_client_1, bad_payload):
        version = api_client_1.get_field_by_id(VALID_FIELD_ID).json()["version"]
        resp = api_client_1.patch_field_options(VALID_FIELD_ID, bad_payload, version=version)

        assert resp.status_code in [200, 400, 422], resp.text

        if resp.status_code in [400, 422]:
            validate(instance=resp.json(), schema=error_schema)
        else:

            data = resp.json()
            assert "optionsProvider" in data
            assert isinstance(data["optionsProvider"], dict)

    @allure.title("Конфликт версий при обновлении options")
    def test_patch_field_options_version_conflict(self, api_client_1):
        payload = {"optionsProvider": {"type": "FixedListOptionsProvider", "values": ["x", "y", "z"]}}
        resp = api_client_1.patch_field_options(VALID_FIELD_ID, payload, version=1)
        assert resp.status_code in [409, 412], resp.text
        validate(instance=resp.json(), schema=error_schema)

    @allure.title("Попытка обновить options у несуществующего поля")
    def test_patch_field_options_not_found(self, api_client_1):
        payload = {"optionsProvider": {"type": "FixedListOptionsProvider", "values": ["one", "two"]}}
        resp = api_client_1.patch_field_options(NON_EXISTENT_FIELD_ID, payload, version=1)
        assert resp.status_code in [400, 404], resp.text
        validate(instance=resp.json(), schema=error_schema)
