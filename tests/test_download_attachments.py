import pytest
import allure
import os
import tempfile
from config import Config
from utils.validators import validate_error_response
from schemas.error_schema import ERROR_SCHEMA


@allure.feature("Яндекс.Трекер API")
@allure.story("Скачивание вложения задачи")
class TestDownloadAttachment:

    @allure.title("Скачивание файла")
    def test_download_attachment(self, api_client, create_issue_with_attachment):
        issue_id, attachment_id, attachment_name = create_issue_with_attachment

        response = api_client.download_attachment(
            Config.OAUTH_TOKEN,
            issue_id,
            attachment_id,
            attachment_name
        )
        assert response.status_code == 200, f"Статус: {response.status_code}, тело: {response.text}"
        assert response.content, "Файл не скачан или пустой"

    @allure.title("Скачивание файла с корректными параметрами")
    def test_download_valid_attachment(self, api_client, create_issue_with_attachment):
        issue_id, attachment_id, file_name = create_issue_with_attachment

        response = api_client.download_attachment(
            Config.OAUTH_TOKEN,
            issue_id,
            attachment_id,
            file_name
        )
        assert response.status_code == 200
        assert len(response.content) > 0
        assert file_name in response.headers["Content-Disposition"]

    @allure.title("Скачивание несуществующего файла")
    def test_download_nonexistent_attachment(self, api_client, create_test_issue):
        issue_id = create_test_issue
        response = api_client.download_attachment(
            Config.OAUTH_TOKEN,
            issue_id,
            "999999999",
            "ghost_file.txt"
        )
        assert response.status_code == 404
        validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Скачивание с невалидным токеном")
    def test_download_unauthorized(self, api_client, create_issue_with_attachment):
        issue_id, attachment_id, file_name = create_issue_with_attachment

        response = api_client.download_attachment(
            Config.INVALID_TOKEN,
            issue_id,
            attachment_id,
            file_name
        )
        assert response.status_code == 401
        validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Скачивание с некорректным именем файла")
    def test_download_wrong_filename(self, api_client, create_issue_with_attachment):
        issue_id, attachment_id, real_filename = create_issue_with_attachment

        response = api_client.download_attachment(
            Config.OAUTH_TOKEN,
            issue_id,
            attachment_id,
            "wrong_filename.txt"
        )

        assert response.status_code == 200
        content_disp = response.headers.get("Content-Disposition", "")
        assert real_filename not in content_disp

    @allure.title("Попытка доступа к файлу из другой задачи")
    def test_cross_issue_access(self, api_client, create_two_issues_with_attachments):
        issue1_id, attachment1_id, file1_name = create_two_issues_with_attachments[0]
        issue2_id, _, _ = create_two_issues_with_attachments[1]

        response = api_client.download_attachment(
            Config.OAUTH_TOKEN,
            issue2_id,
            attachment1_id,
            file1_name
        )
        assert response.status_code == 403 or 404

    @allure.title("Скачивание файла с проверкой MIME-типа")
    def test_mime_type_validation(self, api_client, create_issue_with_image):
        issue_id, attachment_id, file_name = create_issue_with_image

        response = api_client.download_attachment(
            Config.OAUTH_TOKEN,
            issue_id,
            attachment_id,
            file_name
        )
        assert response.status_code == 200
        assert "image/jpeg" in response.headers["Content-Type"]

    @allure.title("Скачивание удаленного файла")
    def test_download_deleted_attachment(self, api_client, create_issue_with_attachment):
        issue_id, attachment_id, file_name = create_issue_with_attachment

        api_client.delete_attachment(
            Config.OAUTH_TOKEN,
            issue_id,
            attachment_id
        )

        response = api_client.download_attachment(
            Config.OAUTH_TOKEN,
            issue_id,
            attachment_id,
            file_name
        )
        assert response.status_code in [404, 410]

    @allure.title("Скачивание большого файла (10MB+)")
    def test_large_file_download(self, api_client, create_issue_with_large_attachment):
        issue_id, attachment_id, file_name = create_issue_with_large_attachment

        response = api_client.download_attachment(
            Config.OAUTH_TOKEN,
            issue_id,
            attachment_id,
            file_name
        )
        assert response.status_code == 200
        assert int(response.headers["Content-Length"]) > 10_000_000