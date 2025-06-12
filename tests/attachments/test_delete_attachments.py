import pytest
import allure
from config import Config
from utils.validators import validate_error_response
from schemas.error_schema import ERROR_SCHEMA


@allure.feature("Яндекс.Трекер API")
@allure.story("Удаление файлов у задачи")
class TestDeleteAttachment:

    @allure.title("Успешное удаление вложения")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_attachment_success(self, api_client, create_issue_with_attachment):
        issue_id, attachment_id, _ = create_issue_with_attachment
        print(issue_id, attachment_id)
        response = api_client.delete_attachment(
            Config.OAUTH_TOKEN,
            issue_id,
            attachment_id
        )
        assert response.status_code == 204, "Ожидался статус 204 после удаления"

        get_response = api_client.get_attachments(Config.OAUTH_TOKEN, issue_id)
        assert get_response.status_code == 200
        attachments = get_response.json()
        assert not any(att["id"] == attachment_id for att in attachments), "Вложение не было удалено"
    @allure.title("Удаление несуществующего файла")
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_nonexistent_attachment(self, api_client, create_test_issue):
        issue_id = create_test_issue
        invalid_attachment_id = "999999999"

        response = api_client.delete_attachment(
            Config.OAUTH_TOKEN,
            issue_id,
            invalid_attachment_id
        )

        assert response.status_code == 404
        validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Удаление файла с невалидным токеном")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_attachment_unauthorized(self, api_client, create_issue_with_attachment):
        issue_id, attachment_id, _ = create_issue_with_attachment

        response = api_client.delete_attachment(
            Config.INVALID_TOKEN,
            issue_id,
            attachment_id
        )

        assert response.status_code == 401
        validate_error_response(response, ERROR_SCHEMA)

        get_response = api_client.get_attachments(Config.OAUTH_TOKEN, issue_id)
        assert get_response.status_code == 200
        attachments = get_response.json()
        assert any(att["id"] == attachment_id for att in attachments)

    @allure.title("Удаление уже удаленного файла")
    @allure.severity(allure.severity_level.MINOR)
    def test_delete_already_deleted_attachment(self, api_client, create_issue_with_attachment):
        issue_id, attachment_id, _ = create_issue_with_attachment

        first_response = api_client.delete_attachment(
            Config.OAUTH_TOKEN,
            issue_id,
            attachment_id
        )
        assert first_response.status_code == 204

        second_response = api_client.delete_attachment(
            Config.OAUTH_TOKEN,
            issue_id,
            attachment_id
        )
        assert second_response.status_code in [404, 410]

    @allure.title("Удаление файла из несуществующей задачи")
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_attachment_from_nonexistent_issue(self, api_client, create_issue_with_attachment):
        _, attachment_id, _ = create_issue_with_attachment

        response = api_client.delete_attachment(
            Config.OAUTH_TOKEN,
            Config.INVALID_ISSUE_ID,
            attachment_id
        )

        assert response.status_code == 404
        validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Удаление файла с невалидным ID")
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_attachment_with_invalid_id_format(self, api_client, create_test_issue):
        issue_id = create_test_issue
        invalid_attachment_ids = [
            "invalid_id",
            "123.45",
            "0",
            "-100"
        ]

        for attachment_id in invalid_attachment_ids:
            with allure.step(f"Проверка ID: {attachment_id}"):
                response = api_client.delete_attachment(
                    Config.OAUTH_TOKEN,
                    issue_id,
                    attachment_id
                )
                assert response.status_code in [400, 404]
                if response.status_code == 400:
                    validate_error_response(response, ERROR_SCHEMA)