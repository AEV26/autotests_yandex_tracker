import allure
import pytest
from jsonschema import validate

from utils.api_client import TrackerApiClient
from schemas.checklist_schema import checklist_schema, error_schema

@allure.feature("Checklist API")
@allure.story("Удаление чек-листа задачи")
class TestDeleteChecklist:

    @allure.title("Позитивный тест: удаление существующего чек-листа")
    def test_delete_checklist_success(self, api_client_1):
        issue_id = "EDU-13"
        items_to_create = [
            {"text": "Первый пункт", "checked": False},
            {"text": "Второй пункт", "checked": True}
        ]
        for itm in items_to_create:
            resp = api_client_1.post_checklist_item(issue_id, itm)
            assert resp.status_code in [200, 201]

        get_before = api_client_1.get_checklist_items(issue_id)
        assert get_before.status_code == 200
        assert isinstance(get_before.json(), list)
        assert len(get_before.json()) >= 2

        with allure.step("Отправляем DELETE запрос для удаления чек-листа"):
            delete_resp = api_client_1.delete_checklist_items(issue_id)

        with allure.step("Проверяем, что код ответа 200 или 204"):
            assert delete_resp.status_code in [200, 204]

        with allure.step("GET после удаления должен вернуть пустой массив"):
            get_after = api_client_1.get_checklist_items(issue_id)
            assert get_after.status_code == 200
            assert get_after.json() == []

    @allure.title("Неавторизованный доступ при удалении чек-листа")
    def test_delete_checklist_unauthorized(self, unauthorized_client):
        issue_id = "EDU-13"
        response = unauthorized_client.delete_checklist_items(issue_id)

        with allure.step("Проверяем, что код ответа 401"):
            assert response.status_code == 401

        with allure.step("Валидируем структуру ошибки"):
            validate(instance=response.json(), schema=error_schema)

    @allure.title("Попытка удалить чек-лист несуществующей задачи")
    def test_delete_checklist_nonexistent_issue(self, api_client_1):
        issue_id = "NONEXISTENT-999"
        response = api_client_1.delete_checklist_items(issue_id)

        with allure.step("Проверяем, что код ответа 404"):
            assert response.status_code == 404

        with allure.step("Валидируем структуру ошибки"):
            validate(instance=response.json(), schema=error_schema)

    @allure.title("Удаление пустого чек-листа")
    def test_delete_empty_checklist(self, api_client_1):
        issue_id = "EDU-13"
        api_client_1.delete_checklist_items(issue_id)

        with allure.step("Отправляем DELETE на уже пустой чек-лист"):
            response = api_client_1.delete_checklist_items(issue_id)

        with allure.step("Проверяем код ответа (200 или 204)"):
            assert response.status_code in [200, 204]

        with allure.step("Валидируем, что GET всё ещё возвращает пустой массив"):
            get_resp = api_client_1.get_checklist_items(issue_id)
            assert get_resp.status_code == 200
            assert get_resp.json() == []
