import allure
import pytest
from utils.validators import ResponseValidator

@allure.feature("Issues")
@allure.story("Get Issue Transitions")
class TestGetIssueTransitions:
    @allure.title("Позитивный тест: получение переходов для валидного ID задачи")
    def test_get_issue_transitions_valid(self, api_client_2, validator, existing_issue_id):
        with allure.step("Отправка GET-запроса на получение переходов задачи"):
            response = api_client_2.get_issue_transitions(existing_issue_id)

        with allure.step("Проверка кода состояния ответа"):
            assert response.status_code == 200

        with allure.step("Валидация структуры ответа"):
            transitions_data = response.json()
            print(f"Response data: {transitions_data}")
            validator.validate_transitions_response(transitions_data)

        with allure.step("Проверка содержимого ответа"):
            assert isinstance(transitions_data, list)
            assert len(transitions_data) > 0
            for transition in transitions_data:
                assert isinstance(transition, dict)
                assert "id" in transition
                assert "self" in transition
                assert "display" in transition
                assert "to" in transition
                assert isinstance(transition["to"], dict)
                assert "id" in transition["to"]
                assert "key" in transition["to"]
                assert "display" in transition["to"]

                if "screen" in transition:
                    assert isinstance(transition["screen"], dict)
                    assert "id" in transition["screen"]
                    assert "display" in transition["screen"]

    @allure.title("Негативный тест: получение переходов для невалидного ID задачи")
    def test_get_issue_transitions_invalid_id(self, api_client_2, validator):
        with allure.step("Отправка GET-запроса с невалидным ID задачи"):
            response = api_client_2.get_issue_transitions("TASTAEV-177")

        with allure.step("Проверка кода состояния ответа"):
            assert response.status_code == 404

        with allure.step("Валидация структуры ошибки"):
            error = response.json()
            validator.validate_error_response(error)

        with allure.step("Проверка сообщения об ошибке"):
            error_message = str(error).lower()
            assert "задача не существует." in error_message or "invalid" in error_message

    @allure.title("Негативный тест: получение переходов без авторизации")
    def test_get_issue_transitions_without_auth(self, api_client_2, validator, existing_issue_id):
        with allure.step("Отправка GET-запроса без токена авторизации"):
            response = api_client_2.get_issue_transitions(
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

    @allure.title("Негативный тест: получение переходов с некорректным ID организации")
    def test_get_issue_transitions_with_invalid_org_id(self, api_client_2, validator, existing_issue_id):
        with allure.step("Отправка GET-запроса с некорректным ID организации"):
            response = api_client_2.get_issue_transitions(
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