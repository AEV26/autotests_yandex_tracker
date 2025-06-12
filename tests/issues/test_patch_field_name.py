import pytest
import allure
from jsonschema import validate
from schemas.fields_schema import field_by_id_schema
from schemas.checklist_schema import error_schema

VALID_FIELD_ID = "test_field_17da8d"
INVALID_FIELD_ID = "nonexistent_field_999"
VALID_NAME = "Новое имя поля1"
EMPTY_NAME = ""
TOO_LONG_NAME = "A" * 300
INVALID_CHARS_NAME = "@@@###$$$"
OLD_VERSION = 1

def localized(name: str) -> dict:
    return {"ru": name, "en": name}

@allure.feature("Fields API")
@allure.story("Изменение названия поля задачи")
class TestPatchFieldName:

    @allure.title("Позитивный тест: Изменение названия поля с валидными параметрами")
    def test_patch_field_name_success(self, api_client_1):

        resp = api_client_1.get_field_by_id(VALID_FIELD_ID)
        assert resp.status_code == 200
        current_version = resp.json()["version"]


        patch_resp = api_client_1.patch_field_name(
            VALID_FIELD_ID,
            {"name": localized(VALID_NAME)},
            version=current_version
        )
        assert patch_resp.status_code == 200, patch_resp.text


        result = patch_resp.json()
        assert result["name"] == VALID_NAME
        assert result["version"] > current_version
        validate(instance=result, schema=field_by_id_schema)


        get_resp = api_client_1.get_field_by_id(VALID_FIELD_ID)
        assert get_resp.status_code == 200
        assert get_resp.json()["name"] == VALID_NAME

    @allure.title("Негативный тест: Неавторизованный доступ")
    def test_patch_field_name_unauthorized(self, unauthorized_client):
        resp = unauthorized_client.patch_field_name(
            VALID_FIELD_ID,
            {"name": localized(VALID_NAME)},
            version=1
        )
        assert resp.status_code == 401
        validate(instance=resp.json(), schema=error_schema)

    @allure.title("Негативный тест: Ошибка валидации (пустое/слишком длинное имя)")
    @pytest.mark.parametrize("bad_name", [EMPTY_NAME, TOO_LONG_NAME, INVALID_CHARS_NAME])
    def test_patch_field_name_validation_errors(self, api_client_1, bad_name):
        current_version = api_client_1.get_field_by_id(VALID_FIELD_ID).json()["version"]
        resp = api_client_1.patch_field_name(
            VALID_FIELD_ID,
            {"name": localized(bad_name)},
            version=current_version
        )

        if bad_name == INVALID_CHARS_NAME:

            assert resp.status_code == 200, resp.text
            assert api_client_1.get_field_by_id(VALID_FIELD_ID).json()["name"] == bad_name
        else:

            assert resp.status_code == 422, resp.text
            validate(instance=resp.json(), schema=error_schema)

    @allure.title("Негативный тест: Отсутствие параметра version")
    def test_patch_field_name_without_version(self, api_client_1):
        resp = api_client_1.patch_field_name(
            VALID_FIELD_ID,
            {"name": localized(VALID_NAME)},
            version=None
        )

        assert resp.status_code == 428, resp.text
        validate(instance=resp.json(), schema=error_schema)

    @allure.title("Негативный тест: Конфликт версий (устаревшая версия)")
    def test_patch_field_name_version_conflict(self, api_client_1):
        resp = api_client_1.patch_field_name(
            VALID_FIELD_ID,
            {"name": localized(VALID_NAME)},
            version=OLD_VERSION
        )

        assert resp.status_code == 412, resp.text
        validate(instance=resp.json(), schema=error_schema)

    @allure.title("Негативный тест: Несуществующее поле")
    def test_patch_field_name_not_found(self, api_client_1):
        resp = api_client_1.patch_field_name(
            INVALID_FIELD_ID,
            {"name": localized(VALID_NAME)},
            version=1
        )
        assert resp.status_code == 404
        validate(instance=resp.json(), schema=error_schema)
