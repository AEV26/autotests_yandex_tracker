import pytest
import allure
from jsonschema import validate
from schemas.fields_schema import field_by_id_schema
from schemas.checklist_schema import error_schema

EXISTING_FIELD_ID = "test_field_17da8d"

NON_EXISTENT_FIELD_ID = "nonexistent_field_123"

@allure.feature("Fields API")
@allure.story("Получение поля по ID")
class TestGetFieldById:

    @allure.title("Позитивный тест: Получение системного поля summary")
    def test_get_existing_field(self, api_client_1):
        with allure.step(f"Отправляем GET /fields/{EXISTING_FIELD_ID}"):
            response = api_client_1.get_field_by_id(EXISTING_FIELD_ID)
            assert response.status_code == 200

        with allure.step("Валидируем структуру ответа"):
            data = response.json()
            assert "id" in data and data["id"] == EXISTING_FIELD_ID
            assert "type" in data
            assert isinstance(data.get("readonly", False), bool)
            assert isinstance(data.get("visible", True), bool)
            validate(instance=data, schema=field_by_id_schema)

    @allure.title("Негативный тест: Неавторизованный запрос")
    def test_get_field_unauthorized(self, unauthorized_client):
        with allure.step(f"GET без токена /fields/{EXISTING_FIELD_ID}"):
            response = unauthorized_client.get_field_by_id(EXISTING_FIELD_ID)
            assert response.status_code == 401
            validate(instance=response.json(), schema=error_schema)

    @allure.title("Негативный тест: Запрос несуществующего поля")
    def test_get_nonexistent_field(self, api_client_1):
        with allure.step(f"GET несуществующего поля /fields/{NON_EXISTENT_FIELD_ID}"):
            response = api_client_1.get_field_by_id(NON_EXISTENT_FIELD_ID)
            assert response.status_code == 404
            validate(instance=response.json(), schema=error_schema)
