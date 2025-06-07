import pytest
import allure
from jsonschema import validate
from schemas.issue_links_schema import issue_links_list_schema
from schemas.checklist_schema import error_schema


@allure.feature("Issues API")
@allure.story("Получение связей задач")
class TestGetIssueLinks:

    @allure.title("Позитивный тест: получение связей существующей задачи")
    def test_get_links_success(self, api_client):
        issue_id = "TES-1"

        with allure.step("Отправляем GET запрос для получения связей задачи"):
            response = api_client.get_issue_links(issue_id)

        with allure.step("Проверяем, что код ответа 200"):
            assert response.status_code == 200

        with allure.step("Валидируем структуру ответа"):
            data = response.json()
            validate(instance=data, schema=issue_links_list_schema)
            assert isinstance(data, list)

            for link in data:
                assert "direction" in link
                assert "type" in link
                assert "object" in link

    @allure.title("Неавторизованный доступ при получении связей")
    def test_get_links_unauthorized(self, unauthorized_client):
        response = unauthorized_client.get_issue_links("TES-1")

        with allure.step("Проверяем код 401"):
            assert response.status_code == 401

        with allure.step("Валидируем структуру ошибки"):
            validate(instance=response.json(), schema=error_schema)

    @allure.title("Попытка получить связи несуществующей задачи")
    def test_get_links_nonexistent_issue(self, api_client):
        response = api_client.get_issue_links("NONEXISTENT-999")

        with allure.step("Проверяем код 404"):
            assert response.status_code == 404

        with allure.step("Валидируем структуру ошибки"):
            validate(instance=response.json(), schema=error_schema)


    @allure.title("Получение связей задачи без связей")
    def test_get_links_no_links(self, api_client):
        issue_id = "TES-3"

        with allure.step("Отправляем GET запрос"):
            response = api_client.get_issue_links(issue_id)

        with allure.step("Проверяем код 200 и что список пуст"):
            assert response.status_code == 200
            assert response.json() == []
