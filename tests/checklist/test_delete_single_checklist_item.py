import allure
import pytest
from jsonschema import validate

from utils.api_client import TrackerApiClient
from schemas.checklist_schema import checklist_schema, error_schema

@allure.feature("Checklist API")
@allure.story("Удаление отдельного пункта чек-листа задачи")
class TestDeleteSingleChecklistItem:

    @allure.title("Позитивный тест: удаление существующего пункта чек-листа")
    def test_delete_single_item_success(self, api_client_1):
        issue_id = "EDU-13"
        new_item = {"text": "Пункт для удаления", "checked": False}
        create_resp = api_client_1.post_checklist_item(issue_id, new_item)
        assert create_resp.status_code in [200, 201]
        created_items = create_resp.json()["checklistItems"]
        created_item = [it for it in created_items if it["text"] == new_item["text"]][-1]
        item_id = created_item["id"]

        with allure.step("Отправляем DELETE запрос для удаления пункта чек-листа"):
            del_resp = api_client_1.delete_single_checklist_item(issue_id, item_id)

        with allure.step("Проверяем, что код ответа 200 или 204"):
            assert del_resp.status_code in [200, 204]

        with allure.step("GET после удаления должен не содержать удалённый пункт"):
            get_resp = api_client_1.get_checklist_items(issue_id)
            assert get_resp.status_code == 200
            items_after = get_resp.json()
            assert all(it["id"] != item_id for it in items_after)

    @allure.title("Неавторизованный доступ при удалении пункта")
    def test_delete_single_item_unauthorized(self, unauthorized_client):
        issue_id = "EDU-13"
        fake_item_id = "000000000000000000000000"
        response = unauthorized_client.delete_single_checklist_item(issue_id, fake_item_id)

        with allure.step("Проверяем, что код ответа 401"):
            assert response.status_code == 401

        with allure.step("Валидируем структуру ошибки"):
            validate(instance=response.json(), schema=error_schema)

    @allure.title("Удаление несуществующего пункта чек-листа")
    @pytest.mark.parametrize("issue_id, item_id", [
        ("EDU-13", "NONEXISTENT_ITEM_ID"),
        ("NONEXISTENT-999", "000000000000000000")
    ])
    def test_delete_single_item_nonexistent(self, api_client_1, issue_id, item_id):
        response = api_client_1.delete_single_checklist_item(issue_id, item_id)

        with allure.step("Проверяем, что код ответа 400 или 404"):
            assert response.status_code in [400, 404]
        with allure.step("Валидируем структуру ошибки"):
           validate(instance=response.json(), schema=error_schema)
    @allure.title("Пограничный случай: повторное удаление одного и того же пункта")
    def test_delete_single_item_idempotency(self, api_client_1):
        issue_id = "EDU-13"
        new_item = {"text": "Пункт для идемпотентности", "checked": False}
        create_resp = api_client_1.post_checklist_item(issue_id, new_item)
        assert create_resp.status_code in [200, 201]
        item_id = create_resp.json()["checklistItems"][-1]["id"]

        first_del = api_client_1.delete_single_checklist_item(issue_id, item_id)
        assert first_del.status_code in [200, 204]

        second_del = api_client_1.delete_single_checklist_item(issue_id, item_id)
        assert second_del.status_code in [200, 204, 404]

    @allure.title("Пограничный случай: удаление с дополнительными параметрами")
    def test_delete_single_item_with_extra_params(self, api_client_1):
        issue_id = "EDU-13"
        new_item = {"text": "Пункт с параметрами", "checked": False}
        create_resp = api_client_1.post_checklist_item(issue_id, new_item)
        assert create_resp.status_code in [200, 201]
        item_id = create_resp.json()["checklistItems"][-1]["id"]

        with allure.step("DELETE с ненужным параметром в URL"):
            del_resp = api_client_1.delete_single_checklist_item(issue_id, item_id, params={"extra": "value"})

        with allure.step("Код ответа должен быть 200 или 204"):
            assert del_resp.status_code in [200, 204]
        get_resp = api_client_1.get_checklist_items(issue_id)
        assert all(it["id"] != item_id for it in get_resp.json())
