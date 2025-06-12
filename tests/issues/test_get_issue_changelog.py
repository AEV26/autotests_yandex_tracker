import allure
import pytest
from utils.validators import ResponseValidator


@allure.feature("Issues")
@allure.story("Get Issue Changelog")
class TestGetIssueChangelog:
    @allure.title("Позитивный тест: получение истории изменений для валидного ID задачи")
    def test_get_issue_changelog_valid(self, api_client_2, validator, existing_issue_id):
        with allure.step("Отправка GET-запроса на получение истории изменений задачи"):
            response = api_client_2.get_issue_changelog(existing_issue_id)

        with allure.step("Проверка кода состояния ответа"):
            assert response.status_code == 200

        with allure.step("Валидация структуры ответа"):
            changelog_data = response.json()
            print(f"Response data: {changelog_data}")
            validator.validate_changelog_response(changelog_data)

        with allure.step("Проверка содержимого ответа"):
            assert isinstance(changelog_data, list)
            assert len(changelog_data) > 0
            for entry in changelog_data:
                assert "issue" in entry
                assert entry["issue"]["key"].startswith("TESTAST")
                assert "updatedAt" in entry
                assert "updatedBy" in entry
                assert "type" in entry
                assert "fields" in entry
                for field in entry["fields"]:
                    assert "field" in field
                    assert any(key in field for key in ["from", "to"])

    @allure.title("Негативный тест: получение истории изменений для невалидного ID задачи")
    def test_get_issue_changelog_invalid_id(self, api_client_2, validator):
        with allure.step("Отправка GET-запроса с невалидным ID задачи"):
            response = api_client_2.get_issue_changelog("6824d2e7e1d2fd7005a8f437")

        with allure.step("Проверка кода состояния ответа"):
            assert response.status_code == 404

        with allure.step("Валидация структуры ошибки"):
            error = response.json()
            validator.validate_error_response(error)

        with allure.step("Проверка сообщения об ошибке"):
            error_message = str(error).lower()
            assert "задача не существует." in error_message or "invalid" in error_message

    @allure.title("Негативный тест: получение истории изменений без авторизации")
    def test_get_issue_changelog_without_auth(self, api_client_2, validator, existing_issue_id):
        with allure.step("Отправка GET-запроса без токена авторизации"):
            response = api_client_2.get_issue_changelog(
                existing_issue_id,
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

    @allure.title("Негативный тест: получение истории изменений с некорректным ID организации")
    def test_get_issue_changelog_with_invalid_org_id(self, api_client_2, validator, existing_issue_id):
        with allure.step("Отправка GET-запроса с некорректным ID организации"):
            response = api_client_2.get_issue_changelog(
                existing_issue_id,
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