# tests/test_edit_checklist_item.py

import allure
import pytest
from jsonschema import validate

from utils.api_client import TrackerApiClient
from schemas.checklist_schema import error_schema

checklist_item_response_schema = {
    "type": "object",
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
@allure.story("Редактирование пункта чек-листа задачи")
class TestEditChecklistItem:

    @allure.title("Позитивный тест: редактирование пункта чек-листа")
    def test_patch_checklist_item_success(self, api_client):
        issue_id = "EDU-13"
        # 1) Сначала создаём новый пункт, чтобы получить его ID
        new_item = {"text": "Пункт для редактирования", "checked": False}
        create_resp = api_client.post_checklist_item(issue_id, new_item)
        assert create_resp.status_code in [200, 201]
        created_data = create_resp.json()
        assert "checklistItems" in created_data
        created_items = created_data["checklistItems"]
        # найдём последний добавленный пункт
        created_item = [it for it in created_items if it["text"] == new_item["text"]][-1]
        item_id = created_item["id"]

        # 2) Теперь редактируем этот пункт
        updated_payload = {"text": "Отредактированный текст", "checked": True}
        with allure.step("Отправляем PATCH запрос для обновления пункта чек-листа"):
            patch_resp = api_client.patch_checklist_item(issue_id, item_id, updated_payload)

        with allure.step("Проверяем, что код ответа 200"):
            assert patch_resp.status_code == 200

        with allure.step("Валидируем структуру обновлённого пункта"):
            patched_data = patch_resp.json()
            assert "checklistItems" in patched_data
            items_after_patch = patched_data["checklistItems"]
            matching = [it for it in items_after_patch if it["id"] == item_id]
            assert len(matching) == 1
            validate(instance=matching[0], schema=checklist_item_response_schema)
            assert matching[0]["text"] == updated_payload["text"]
            assert matching[0]["checked"] is True

        with allure.step("Проверяем факт изменения через GET"):
            get_resp = api_client.get_checklist_items(issue_id)
            get_items = get_resp.json()
            updated_in_get = [it for it in get_items if it["id"] == item_id][0]
            assert updated_in_get["text"] == updated_payload["text"]
            assert updated_in_get["checked"] is True

    @allure.title("Неавторизованный доступ при редактировании")
    def test_patch_checklist_item_unauthorized(self, unauthorized_client):
        issue_id = "EDU-13"
        fake_item_id = "000000000000000000000000"
        payload = {"text": "Текст", "checked": False}
        response = unauthorized_client.patch_checklist_item(issue_id, fake_item_id, payload)

        with allure.step("Проверяем, что код ответа 401"):
            assert response.status_code == 401

        with allure.step("Валидируем структуру ошибки"):
            validate(instance=response.json(), schema=error_schema)

    @allure.title("Ошибка валидации при редактировании")
    @pytest.mark.parametrize("invalid_data", [
        {"text": "", "checked": False},           # пустой текст
        {"text": "Текст", "checked": "не_булево"}, # неверный тип checked
        {"unsupportedField": "value"},             # неподдерживаемое поле
    ])
    def test_patch_checklist_item_validation_error(self, api_client, invalid_data):
        issue_id = "EDU-13"
        # создаём новый пункт для теста валидации
        create_resp = api_client.post_checklist_item(issue_id, {"text": "Для валидации", "checked": False})
        assert create_resp.status_code in [200, 201]
        created_items = create_resp.json()["checklistItems"]
        item_id = [it for it in created_items if it["text"] == "Для валидации"][-1]["id"]

        response = api_client.patch_checklist_item(issue_id, item_id, invalid_data)

        with allure.step("Проверяем код ответа (200, 400 или 422)"):
            assert response.status_code in [200, 400, 422]

        with allure.step("Валидируем структуру ошибки (если 400 или 422)"):
            if response.status_code in [400, 422]:
                validate(instance=response.json(), schema=error_schema)

    @allure.title("Попытка редактировать несуществующий пункт")
    def test_patch_checklist_item_nonexistent(self, api_client):
        issue_id = "EDU-13"
        fake_item_id = "NONEXISTENT_ITEM_ID"
        payload = {"text": "Текст", "checked": False}
        response = api_client.patch_checklist_item(issue_id, fake_item_id, payload)

        with allure.step("Проверяем код ответа (400 или 404)"):
            assert response.status_code in [400, 404]

        with allure.step("Валидируем структуру ошибки"):
            validate(instance=response.json(), schema=error_schema)

    @allure.title("Частичное обновление (только текст)")
    def test_patch_checklist_item_partial_update_text(self, api_client):
        issue_id = "EDU-13"
        # создаём пункт для частичного обновления
        create_resp = api_client.post_checklist_item(issue_id, {"text": "Частичный", "checked": False})
        assert create_resp.status_code in [200, 201]
        item = create_resp.json()["checklistItems"][-1]
        item_id = item["id"]

        # обновляем только текст
        with allure.step("PATCH: обновляем только текст"):
            patch_resp = api_client.patch_checklist_item(issue_id, item_id, {"text": "Только текст"})

        with allure.step("Код 200 и проверка поля text"):
            assert patch_resp.status_code == 200
            patched = [it for it in patch_resp.json()["checklistItems"] if it["id"] == item_id][0]
            assert patched["text"] == "Только текст"
            assert "checked" in patched  # checked должно остаться без изменений

    @allure.title("Частичное обновление (только checked)")
    def test_patch_checklist_item_partial_update_checked(self, api_client):
        issue_id = "EDU-13"
        create_resp = api_client.post_checklist_item(issue_id, {"text": "Частичный2", "checked": False})
        assert create_resp.status_code in [200, 201]
        item = create_resp.json()["checklistItems"][-1]
        item_id = item["id"]

        # обновляем только checked
        with allure.step("PATCH: обновляем только checked"):
            patch_resp = api_client.patch_checklist_item(issue_id, item_id, {"checked": True})

        with allure.step("Код 200 и проверка поля checked"):
            assert patch_resp.status_code == 200
            patched = [it for it in patch_resp.json()["checklistItems"] if it["id"] == item_id][0]
            assert patched["checked"] is True
            assert "text" in patched  # text должно остаться прежним
