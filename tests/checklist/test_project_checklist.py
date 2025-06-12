import pytest
import allure
from jsonschema import validate
from schemas.checklist_schema import error_schema

ENTITY_TYPE = "project"
PROJECT_ID = "5"
INVALID_PROJECT_ID = "nonexistent_project"

@allure.feature("Checklist Items")
@allure.story("POST /v3/entities/project/<id>/checklistItems")
class TestChecklistItems:

    @allure.title("Успешное добавление одного чеклист-элемента (проверка только кода)")
    def test_create_checklist_item_success(self, api_client_1):
        payload = {
            "text": "Первый пункт",
            "checked": False,
        }
        with allure.step("POST запрос к API"):
            response = api_client_1.post_project_checklist_item(ENTITY_TYPE, PROJECT_ID, payload)

        with allure.step("Проверка кода ответа"):
            assert response.status_code == 200


    @allure.title("Добавление нескольких пунктов чеклиста")
    def test_create_multiple_checklist_items(self, api_client_1):
        payload = [
            {"text": "Пункт 1"},
            {"text": "Пункт 2", "checked": True}
        ]
        response = api_client_1.post_multiple_project_checklist_items(ENTITY_TYPE, PROJECT_ID, payload)
        assert response.status_code == 200
        assert "entityType" in response.json()

    @allure.title("Попытка создания без авторизации")
    def test_create_checklist_item_unauthorized(self, unauthorized_client):
        payload = {"text": "Без токена", "checked": False}
        response = unauthorized_client.post_project_checklist_item(ENTITY_TYPE, PROJECT_ID, payload)
        assert response.status_code == 401
        validate(instance=response.json(), schema=error_schema)

    @allure.title("Валидация: пустой текст, неправильный тип и отсутствие полей")
    @pytest.mark.parametrize("payload", [
        {"text": "", "checked": True},
        {"text": "Неверный тип", "checked": "yes"},
        {}
    ])
    def test_create_checklist_item_invalid(self, api_client_1, payload):
        response = api_client_1.post_project_checklist_item(ENTITY_TYPE, PROJECT_ID, payload)
        assert response.status_code in (400, 422)
        validate(instance=response.json(), schema=error_schema)

    @allure.title("Добавление в несуществующий проект")
    def test_create_checklist_item_invalid_project(self, api_client_1):
        payload = {"text": "Не туда", "checked": False}
        response = api_client_1.post_project_checklist_item(ENTITY_TYPE, INVALID_PROJECT_ID, payload)
        assert response.status_code in (400, 404)
        validate(instance=response.json(), schema=error_schema)
