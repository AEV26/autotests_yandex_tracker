import allure
import pytest
from utils.validators import ResponseValidator

@allure.feature("Issues")
@allure.story("Search Issues")
class TestSearchIssues:
    @allure.title("Позитивный тест: поиск задач по валидному фильтру в очереди TESTAEV без исполнителя")
    def test_search_issues_valid_filter(self, api_client_2, validator):
        search_params = {
            "filter": {
                "queue": "TESTAST",
                "assignee": "empty()"
            },
            "order":"+status"
        }

        with allure.step("Отправка POST-запроса на поиск задач"):
            response = api_client_2.search_issues(search_params)

        with allure.step("Проверка кода состояния ответа"):
            assert response.status_code == 200

        with allure.step("Валидация структуры ответа"):
            search_data = response.json()
            print(f"Response data: {search_data}")
            validator.validate_search_response(search_data)

        with allure.step("Проверка содержимого ответа"):
            assert isinstance(search_data, list)
            for issue in search_data:
                assert "id" in issue
                assert "key" in issue
                assert "summary" in issue
                assert issue["queue"]["key"] == "TESTAST"
                assert "assignee" not in issue or issue["assignee"] is None

    @allure.title("Негативный тест: поиск задач без авторизации")
    def test_search_issues_without_auth(self, api_client_2, validator):
        search_params = {
            "filter": {
                "queue": "TESTAST"
            }
        }

        with allure.step("Отправка POST-запроса без токена авторизации"):
            response = api_client_2.search_issues(
                search_params,
                headers={"Authorization": None, "X-Cloud-Org-ID": None}
            )

        with allure.step("Проверка кода состояния ответа"):
            assert response.status_code == 401

        with allure.step("Валидация структуры ошибки"):
            try:
                error = response.json()
                validator.validate_error_response(error)
                error_message = str(error).lower()
            except ValueError:
                error_message = response.text.lower()

            with allure.step("Проверка сообщения об ошибке"):
                assert any(phrase in error_message
                           for phrase in ["unauthorized", "authorization required", "authentication"])

    @allure.title("Негативный тест: поиск задач с некорректным ID организации")
    def test_search_issues_with_invalid_org_id(self, api_client_2, validator):
        search_params = {
            "filter": {
                "queue": "TESTAST"
            }
        }

        with allure.step("Отправка POST-запроса с некорректным ID организации"):
            response = api_client_2.search_issues(
                search_params,
                headers={"X-Cloud-Org-ID": "invalid"}
            )

        with allure.step("Проверка кода состояния ответа"):
            assert response.status_code == 403

        with allure.step("Валидация структуры ошибки"):
            error = response.json()
            validator.validate_error_response(error)

        with allure.step("Проверка сообщения об ошибке"):
            error_message = str(error).lower()
            assert any(word in error_message
                       for word in ["permission", "organization", "not available"])

    @allure.title("Негативный тест: поиск задач с некорректным фильтром")
    def test_search_issues_invalid_filter(self, api_client_2, validator):
        search_params = {
            "filter": {
                "queue": "TEST"
            }
        }

        with allure.step("Отправка POST-запроса с некорректным фильтром"):
            response = api_client_2.search_issues(search_params)

        with allure.step("Проверка кода состояния ответа"):
            assert response.status_code == 200

        with allure.step("Валидация структуры ответа"):
            search_data = response.json()
            print(f"Response data with invalid filter: {search_data}")
            validator.validate_search_response(search_data)

        with allure.step("Проверка содержимого ответа"):
            assert isinstance(search_data, list)
            assert len(search_data) == 0