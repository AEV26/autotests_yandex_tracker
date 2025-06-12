import allure
import pytest
from utils.validators import ResponseValidator

@allure.feature("Issues")
@allure.story("Count Issues")
class TestCountIssues:
    @allure.title("Получение количества задач по валидному фильтру с очередью и без исполнителя")
    def test_get_issue_count_valid_filter(self, api_client_2, validator):
        filter_params = {
            "filter": {
                "queue": "TESTAST",
                "assignee": "empty()"
            }
        }

        with allure.step("Отправка POST-запроса на подсчет задач"):
            response = api_client_2.get_issue_count(filter_params)

        with allure.step("Проверка кода состояния ответа"):
            assert response.status_code == 200

        with allure.step("Валидация структуры ответа"):
            count_data = response.json()
            print(f"Response data: {count_data}")
            validator.validate_count_response(count_data)

        with allure.step("Проверка содержимого ответа"):
            assert isinstance(count_data, (int, float))
            assert count_data >= 0

    @allure.title("Получение количества задач без авторизации")
    def test_get_issue_count_without_auth(self, api_client_2, validator):
        filter_params = {
            "filter": {
                "queue": "TESTAST",
                "assignee": "empty()"
            }
        }

        with allure.step("Отправка POST-запроса без токена авторизации"):
            response = api_client_2.get_issue_count(
                filter_params,
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

    @allure.title("Получение количества задач с некорректным ID организации")
    def test_get_issue_count_with_invalid_org_id(self, api_client_2, validator):
        filter_params = {
            "filter": {
                "queue": "TESTAST",
                "assignee": "empty()"
            }
        }

        with allure.step("Отправка POST-запроса с некорректным ID организации"):
            response = api_client_2.get_issue_count(
                filter_params,
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

    @allure.title("Получение количества задач с некорректным фильтром")
    def test_get_issue_count_invalid_filter(self, api_client_2, validator):
        filter_params = {
            "filter": {
                "queue": "TEST",
                "assignee": "empty()"
            }
        }

        with allure.step("Отправка POST-запроса с некорректным фильтром"):
            response = api_client_2.get_issue_count(filter_params)

        with allure.step("Проверка кода состояния ответа"):
            assert response.status_code == 200

        with allure.step("Валидация структуры ответа"):
            count_data = response.json()
            print(f"Response data with invalid filter: {count_data}")
            validator.validate_count_response(count_data)

        with allure.step("Проверка содержимого ответа"):
            assert isinstance(count_data, (int, float))
            print(f"Count for invalid queue: {count_data}")
