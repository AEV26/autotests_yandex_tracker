import pytest
import allure
from config import Config
from utils.validators import validate_response_schema, validate_error_response
from schemas.attachment_schema import ATTACHMENT_LIST_SCHEMA
from schemas.error_schema import ERROR_SCHEMA
import time


@allure.feature("Яндекс.Трекер API")
@allure.story("Получение списка прикрепленных файлов")
class TestGetAttachments:

    @allure.title("Получение списка файлов существующей задачи")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_attachments_success(self, api_client, issue_with_attachments):
        issue_id, expected_files = issue_with_attachments

        import time
        time.sleep(2)

        with allure.step("Запрашиваем список файлов"):
            response = api_client.get_attachments(Config.OAUTH_TOKEN, issue_id)

        with allure.step("Проверяем ответ"):
            assert response.status_code == 200, f"Ожидался код 200, получен {response.status_code}. Ответ: {response.text}"
            validate_response_schema(response, ATTACHMENT_LIST_SCHEMA)

            attachments = response.json()
            assert len(attachments) == len(expected_files), (
                f"Ожидалось {len(expected_files)} файлов, получено {len(attachments)}"
            )

            received_names = {a["name"] for a in attachments}
            for expected_name in expected_files:
                assert expected_name in received_names, (
                    f"Файл {expected_name} отсутствует в ответе"
                )

    @allure.title("Неавторизованный доступ")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_attachments_unauthorized(self, api_client, issue_with_attachments):
        issue_id, _ = issue_with_attachments

        response = api_client.get_attachments("invalid_token", issue_id)

        assert response.status_code == 401
        validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Запрос для несуществующей задачи")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_attachments_not_found(self, api_client):
        response = api_client.get_attachments(Config.OAUTH_TOKEN, "INVALID-123")

        assert response.status_code == 404
        validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Задача без прикрепленных файлов")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_attachments_empty(self, api_client, create_test_issue):
        issue_id = create_test_issue

        response = api_client.get_attachments(Config.OAUTH_TOKEN, issue_id)

        assert response.status_code == 200
        assert response.json() == []