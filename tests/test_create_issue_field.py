import pytest
import allure
import uuid
from jsonschema import validate
from schemas.fields_schema import global_fields_schema
from schemas.checklist_schema import error_schema


def get_existing_category(api_client) -> str:
    response = api_client.get_global_fields()
    assert response.status_code == 200, "Не удалось получить список полей"
    for field in response.json():
        if "category" in field and isinstance(field["category"], dict):
            return field["category"]["id"]
    raise ValueError("Не найдена ни одна категория с ID")


@allure.feature("Fields API")
@allure.story("Создание пользовательского поля")
class TestCreateIssueField:

    @allure.title("Позитивный тест: создание текстового поля")
    def test_create_field_success(self, api_client):
        category_id = get_existing_category(api_client)
        suffix = uuid.uuid4().hex[:6]
        unique_id = f"test_field_{suffix}"
        payload = {
            "name": {
                "ru": f"Тестовое поле {suffix}",
                "en": f"Test Field {suffix}"
            },
            "id": unique_id,
            "type": "ru.yandex.startrek.core.fields.StringFieldType",
            "category": category_id
        }

        with allure.step("Отправляем POST запрос на создание поля"):
            response = api_client.create_issue_field(payload)

        with allure.step("Проверяем код ответа"):
            assert response.status_code in [200, 201], response.text

        with allure.step("Проверяем структуру ответа"):
            data = response.json()
            assert data["id"] == payload["id"]
            assert data["type"] in [payload["type"], "standard"]
            validate(instance=data, schema=global_fields_schema)

    @allure.title("Неавторизованный доступ")
    def test_create_field_unauthorized(self, unauthorized_client, api_client):
        category_id = get_existing_category(api_client)
        suffix = uuid.uuid4().hex[:6]
        payload = {
            "name": {
                "ru": f"Поле без токена {suffix}",
                "en": f"Field without token {suffix}"
            },
            "id": f"unauth_field_{suffix}",
            "type": "ru.yandex.startrek.core.fields.StringFieldType",
            "category": category_id
        }

        with allure.step("Отправляем POST без авторизации"):
            response = unauthorized_client.create_issue_field(payload)

        with allure.step("Проверяем 401 и структуру ошибки"):
            assert response.status_code == 401
            validate(instance=response.json(), schema=error_schema)

    @allure.title("Ошибка валидации: невалидный тип поля")
    def test_create_field_invalid_type(self, api_client):
        category_id = get_existing_category(api_client)
        suffix = uuid.uuid4().hex[:6]
        payload = {
            "name": {
                "ru": f"Невалидное поле {suffix}",
                "en": f"Invalid Field {suffix}"
            },
            "id": f"invalid_type_{suffix}",
            "type": "invalid_type_name",
            "category": category_id
        }

        with allure.step("Отправляем POST с невалидным типом"):
            response = api_client.create_issue_field(payload)
            assert response.status_code in [400, 422], response.text
            validate(instance=response.json(), schema=error_schema)

    @allure.title("Ошибка валидации: пустое имя поля")
    def test_create_field_empty_name(self, api_client):
        category_id = get_existing_category(api_client)
        payload = {
            "name": {
                "ru": "",
                "en": ""
            },
            "id": f"empty_name_{uuid.uuid4().hex[:6]}",
            "type": "ru.yandex.startrek.core.fields.StringFieldType",
            "category": category_id
        }

        with allure.step("Отправляем POST с пустым именем"):
            response = api_client.create_issue_field(payload)
            assert response.status_code in [400, 422], response.text
            validate(instance=response.json(), schema=error_schema)

    @allure.title("Конфликт: повторное создание поля с тем же ID")
    def test_create_field_conflict(self, api_client):
        category_id = get_existing_category(api_client)
        suffix = uuid.uuid4().hex[:6]
        field_id = f"conflict_field_{suffix}"
        payload = {
            "name": {
                "ru": f"Дубликат {suffix}",
                "en": f"Duplicate {suffix}"
            },
            "id": field_id,
            "type": "ru.yandex.startrek.core.fields.StringFieldType",
            "category": category_id
        }

        with allure.step("Создаём поле первый раз"):
            first_response = api_client.create_issue_field(payload)
            assert first_response.status_code in [200, 201, 409], first_response.text

        with allure.step("Пробуем создать поле повторно"):
            second_response = api_client.create_issue_field(payload)
            assert second_response.status_code == 422, second_response.text
            validate(instance=second_response.json(), schema=error_schema)
