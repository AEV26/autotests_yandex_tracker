import allure
import pytest
from utils.validators import ResponseValidator

@allure.feature("Issues")
@allure.story("Move Issue")
class TestMoveIssue:
    @allure.title("Позитивный тест: успешное перемещение задачи с валидным ID и ключом очереди")
    def test_move_issue_valid(self, api_client_2, validator, existing_issue_id):
        target_queue = "TESTEGOR"
        move_data = {"description": "Moved to TESTEGOR by API"}

        with allure.step("Отправка POST-запроса на перемещение задачи"):
            response = api_client_2.move_issue(existing_issue_id, target_queue, move_data)

        with allure.step("Проверка кода состояния ответа"):
            assert response.status_code == 200

        with allure.step("Валидация структуры ответа"):
            move_result = response.json()
            print(f"Response data: {move_result}")
            validator.validate_move_response(move_result)

        with allure.step("Проверка содержимого ответа"):
            assert "id" in move_result
            assert move_result["id"] == existing_issue_id
            assert "queue" in move_result
            assert move_result["queue"]["key"] == target_queue
            assert "description" in move_result
            assert move_result["description"] == move_data["description"]

    @allure.title("Негативный тест: перемещение задачи с невалидным ID и валидным ключом очереди")
    def test_move_issue_invalid_id(self, api_client_2, validator):
        target_queue = "TESTEGOR"
        move_data = {}

        with allure.step("Отправка POST-запроса с невалидным ID задачи"):
            response = api_client_2.move_issue("6824d2e7e1d2fd7005a8f437", target_queue, move_data)

        with allure.step("Проверка кода состояния ответа"):
            assert response.status_code == 404

        with allure.step("Валидация структуры ошибки"):
            error = response.json()
            validator.validate_error_response(error)

        with allure.step("Проверка сообщения об ошибке"):
            error_message = str(error).lower()
            assert "задача не существует." in error_message or "invalid" in error_message

    @allure.title("Негативный тест: перемещение задачи с валидным ID и невалидным ключом очереди")
    def test_move_issue_invalid_queue(self, api_client_2, validator, existing_issue_id):
        target_queue = "INVALIDQUEUE"
        move_data = {}

        with allure.step("Отправка POST-запроса с невалидным ключом очереди"):
            response = api_client_2.move_issue(existing_issue_id, target_queue, move_data)

        with allure.step("Проверка кода состояния ответа"):
            assert response.status_code == 404

        with allure.step("Валидация структуры ошибки"):
            error = response.json()
            validator.validate_error_response(error)

        with allure.step("Проверка сообщения об ошибке"):
            error_message = str(error).lower()
            assert "queue invalidqueue was not found" in error_message

    @allure.title("Негативный тест: перемещение задачи без авторизации")
    def test_move_issue_without_auth(self, api_client_2, validator, existing_issue_id):
        target_queue = "TESTEGOR"
        move_data = {}

        with allure.step("Отправка POST-запроса без токена авторизации"):
            response = api_client_2.move_issue(
                existing_issue_id,
                target_queue,
                move_data,
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

    @allure.title("Негативный тест: перемещение задачи с некорректным ID организации")
    def test_move_issue_with_invalid_org_id(self, api_client_2, validator, existing_issue_id):
        target_queue = "TESTEGOR"
        move_data = {}

        with allure.step("Отправка POST-запроса с некорректным ID организации"):
            response = api_client_2.move_issue(
                existing_issue_id,
                target_queue,
                move_data,
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