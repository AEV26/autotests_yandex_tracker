import pytest
import allure
from jsonschema import validate
from schemas.fields_schema import global_fields_schema
from schemas.checklist_schema import error_schema


@allure.feature("Fields API")
@allure.story("Получение глобальных полей")
class TestGetGlobalFields:

    @allure.title("Позитивный тест: получение списка глобальных полей")
    def test_get_global_fields_success(self, api_client_1):
        with allure.step("Отправляем GET запрос для получения глобальных полей"):
            response = api_client_1.get_global_fields()
        with allure.step("Проверяем, что код ответа 200"):
            assert response.status_code == 200
        with allure.step("Валидируем структуру ответа"):
            data = response.json()
            assert isinstance(data, list)
            for field in data:
                validate(instance=field, schema=global_fields_schema)

    @allure.title("Неавторизованный доступ при получении полей")
    def test_get_global_fields_unauthorized(self, unauthorized_client):
        response = unauthorized_client.get_global_fields()
        with allure.step("Проверяем код 401"):
            assert response.status_code == 401
        with allure.step("Валидируем структуру ошибки"):
            validate(instance=response.json(), schema=error_schema)


