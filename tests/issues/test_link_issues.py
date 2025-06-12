import pytest
import allure
from jsonschema import validate
from utils.api_client import TrackerApiClient
from schemas.checklist_schema import error_schema
from schemas.issue_links_schema import issue_link_schema


@allure.feature("Issues API")
@allure.story("Связывание задач")
class TestIssueLinking:

    @allure.title("Позитивный тест: связывание двух задач")
    def test_link_issues_success(self, api_client_1):
        source_id = "TES-1"
        target_id = "TES-2"
        payload = {
            "relationship": "relates",
            "issue": {"key": target_id}
        }

        with allure.step("Отправляем POST запрос для создания связи"):
            response = api_client_1.link_issues(source_id, payload)

        with allure.step(f"Проверяем, что код ответа 201 или 422: {response.status_code}"):
            assert response.status_code in [201, 422]

        if response.status_code == 201:
            with allure.step("Валидируем структуру ответа"):
                body = response.json()
                validate(instance=body, schema=issue_link_schema)
                assert body["object"]["key"] == target_id
                assert body["type"]["id"] == "relates"

    @allure.title("Неавторизованный доступ при связывании")
    def test_link_issues_unauthorized(self, unauthorized_client):
        response = unauthorized_client.link_issues("TES-1", {
            "relationship": "relates",
            "issue": {"key": "TES-2"}
        })

        with allure.step("Проверяем код 401"):
            assert response.status_code == 401
        validate(instance=response.json(), schema=error_schema)

    @allure.title("Ошибка валидации при связывании")
    @pytest.mark.parametrize("payload", [
        {"relationship": "nonexistent", "issue": {"key": "TES-2"}},
        {"relationship": "relates", "issue": {"key": ""}},
        {"relationship": "relates"},
        {}
    ])
    def test_link_issues_validation_error(self, api_client_1, payload):
        response = api_client_1.link_issues("TES-1", payload)
        assert response.status_code in [400, 422]
        validate(instance=response.json(), schema=error_schema)

    @allure.title("Связывание с несуществующей задачей")
    def test_link_issues_nonexistent(self, api_client_1):
        payload = {"relationship": "relates", "issue": {"key": "NONEXISTENT-999"}}
        response = api_client_1.link_issues("TES-1", payload)
        assert response.status_code == 404
        validate(instance=response.json(), schema=error_schema)

    @allure.title("Попытка связать задачу с самой собой")
    def test_link_issue_to_itself(self, api_client_1):
        issue_id = "TES-1"
        payload = {"relationship": "relates", "issue": {"key": issue_id}}
        response = api_client_1.link_issues(issue_id, payload)
        assert response.status_code in [400, 409, 422]
        validate(instance=response.json(), schema=error_schema)

    @allure.title("Попытка создать дублирующую связь")
    def test_duplicate_link(self, api_client_1):
        issue_id = "TES-1"
        target_id = "TES-2"
        payload = {"relationship": "relates", "issue": {"key": target_id}}

        first = api_client_1.link_issues(issue_id, payload)
        assert first.status_code in [201, 422]

        second = api_client_1.link_issues(issue_id, payload)
        assert second.status_code in [409, 422]

