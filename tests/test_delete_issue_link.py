import pytest
import allure
from jsonschema import validate
from schemas.checklist_schema import error_schema


@allure.feature("Issues API")
@allure.story("Удаление связей задач")
class TestDeleteIssueLink:

    @allure.title("Позитивный тест: удаление существующей связи")
    def test_delete_issue_link_success(self, api_client):
        issue_id = "TES-1"
        target_id = "TES-3"
        payload = {
            "relationship": "relates",
            "issue": {"key": target_id}
        }

        with allure.step("Создаём связь между задачами"):
            link_resp = api_client.link_issues(issue_id, payload)
            assert link_resp.status_code in [201, 409]
            link_id = link_resp.json().get("id") if link_resp.status_code == 201 else api_client.find_link_id(issue_id, target_id)

        with allure.step("Удаляем связь"):
            del_resp = api_client.delete_issue_link(issue_id, link_id)
            assert del_resp.status_code == 204

        with allure.step("Проверяем, что связь удалена"):
            links = api_client.get_issue_links(issue_id).json()
            assert all(link["id"] != link_id for link in links)

    @allure.title("Неавторизованный доступ при удалении связи")
    def test_delete_link_unauthorized(self, unauthorized_client):
        issue_id = "TES-1"
        link_id = "1"  # может быть фиктивным

        with allure.step("Пытаемся удалить связь без авторизации"):
            response = unauthorized_client.delete_issue_link(issue_id, link_id)

        with allure.step("Ожидаем 401"):
            assert response.status_code == 401
            validate(instance=response.json(), schema=error_schema)

    @allure.title("Удаление несуществующей связи")
    @pytest.mark.parametrize("issue_id, link_id", [
        ("TES-1", "999999999"),          # несуществующий link_id
        ("NONEXISTENT-999", "1"),        # несуществующий issue_id
    ])
    def test_delete_nonexistent_link(self, api_client, issue_id, link_id):
        with allure.step(f"Пытаемся удалить несуществующую связь {link_id} у задачи {issue_id}"):
            response = api_client.delete_issue_link(issue_id, link_id)

        with allure.step("Ожидаем 404"):
            assert response.status_code == 404
            validate(instance=response.json(), schema=error_schema)

    @allure.title("Повторное удаление уже удалённой связи")
    def test_delete_link_twice(self, api_client):
        issue_id = "TES-1"
        target_id = "TES-4"
        payload = {
            "relationship": "relates",
            "issue": {"key": target_id}
        }

        with allure.step("Создаём связь"):
            link_resp = api_client.link_issues(issue_id, payload)
            assert link_resp.status_code in [201, 409]
            link_id = link_resp.json().get("id") if link_resp.status_code == 201 else api_client.find_link_id(issue_id, target_id)

        with allure.step("Удаляем связь"):
            del_resp = api_client.delete_issue_link(issue_id, link_id)
            assert del_resp.status_code == 204

        with allure.step("Удаляем связь повторно"):
            second_del = api_client.delete_issue_link(issue_id, link_id)
            assert second_del.status_code in [404, 204]
