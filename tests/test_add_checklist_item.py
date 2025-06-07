# tests/test_add_checklist_item.py

import allure
import pytest
from jsonschema import validate

from utils.api_client import TrackerApiClient
from schemas.checklist_schema import error_schema

checklist_item_response_schema = {
    "type": "object",
    # теперь обязательны только id, text, checked, checklistItemType
    "required": ["id", "text", "checked", "checklistItemType"],
    "properties": {
        "id": {"type": "string"},
        "text": {"type": "string"},
        "checked": {"type": "boolean"},
        "checklistItemType": {"type": "string"},
        "assignee": {
            "oneOf": [
                {"type": "null"},
                {
                    "type": "object",
                    "required": ["id", "display"],
                    "properties": {
                        "id": {"type": ["string", "number"]},
                        "display": {"type": "string"}
                    },
                    "additionalProperties": True
                }
            ]
        },
        "deadline": {
            "oneOf": [
                {"type": "null"},
                {
                    "type": "object",
                    "properties": {
                        "date": {"type": "string"},
                        "deadlineType": {"type": "string"},
                        "isExceeded": {"type": "boolean"}
                    },
                    "additionalProperties": True
                }
            ]
        }
    },
    "additionalProperties": True
}


@allure.feature("Checklist API")
@allure.story("Добавление пункта в чек-лист задачи")
class TestAddChecklistItem:

    @allure.title("Позитивный тест: создание нового пункта чек-листа")
    def test_create_checklist_item_success(self, api_client):
        issue_id = "EDU-13"
        new_item = {
            "text": "Новый пункт для автотеста",
            "checked": False
        }
        with allure.step("Отправляем POST запрос на создание пункта чек-листа"):
            response = api_client.post_checklist_item(issue_id, new_item)

        with allure.step("Проверяем, что код ответа 200 или 201"):
            assert response.status_code in [200, 201]

        with allure.step("Валидируем, что в ответе есть поле checklistItems и добавленный пункт"):
            data = response.json()
            assert "checklistItems" in data

            matching_items = [
                item for item in data["checklistItems"]
                if item.get("text") == new_item["text"]
            ]
            assert len(matching_items) > 0

            validate(instance=matching_items[0], schema=checklist_item_response_schema)

        with allure.step("Проверяем, что пункт действительно добавился (GET чек-листа)"):
            get_resp = api_client.get_checklist_items(issue_id)
            assert any(item.get("text") == new_item["text"] for item in get_resp.json())

    @allure.title("Неавторизованный доступ")
    def test_create_checklist_item_unauthorized(self, unauthorized_client):
        issue_id = "EDU-13"
        item = {"text": "Тест", "checked": False}
        response = unauthorized_client.post_checklist_item(issue_id, item)

        with allure.step("Проверяем, что код ответа 401"):
            assert response.status_code == 401

        with allure.step("Валидируем структуру ошибки"):
            validate(instance=response.json(), schema=error_schema)

    @allure.title("Ошибка валидации данных")
    @pytest.mark.parametrize("invalid_data", [
        {"text": "", "checked": False},       # пустой текст
        {"text": "Текст", "checked": "нет"},  # неправильный тип checked
        {},                                   # пустой словарь
    ])
    def test_create_checklist_item_validation_error(self, api_client, invalid_data):
        issue_id = "EDU-13"
        response = api_client.post_checklist_item(issue_id, invalid_data)

        with allure.step("Проверяем, что код ответа 400 или 422"):
            assert response.status_code in [400, 422]

        with allure.step("Валидируем структуру ошибки"):
            validate(instance=response.json(), schema=error_schema)

    @allure.title("Попытка добавить пункт в несуществующую задачу")
    def test_create_checklist_item_nonexistent_issue(self, api_client):
        issue_id = "NONEXISTENT-999"
        item = {"text": "Тест", "checked": False}
        response = api_client.post_checklist_item(issue_id, item)

        with allure.step("Проверяем, что код ответа 404"):
            assert response.status_code == 404

        with allure.step("Валидируем структуру ошибки"):
            validate(instance=response.json(), schema=error_schema)
