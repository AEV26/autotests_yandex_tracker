import pytest
import allure
import os
import tempfile
from config import Config
from utils.validators import validate_error_response
from schemas.error_schema import ERROR_SCHEMA

@allure.feature("Яндекс.Трекер API")
@allure.story("Прикрепление файлов к задаче")
class TestUploadAttachment:

    @allure.title("Успешное прикрепление файла к задаче")
    def test_upload_attachment_success(self, api_client, create_test_issue):
        issue_id = create_test_issue

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
            tmp.write(b"Test file content")
            tmp_path = tmp.name
            file_name = os.path.basename(tmp_path)

        with open(tmp_path, "rb") as f:
            files = {"file": (file_name, f)}
            response = api_client.upload_attachment(
                Config.OAUTH_TOKEN,
                issue_id,
                files
            )
        os.unlink(tmp_path)

        assert response.status_code == 201, f"Статус: {response.status_code}, тело: {response.text}"
        data = response.json()
        assert "id" in data
        assert data["name"] == file_name
        assert "content" in data

    @allure.title("Прикрепление файла с невалидным токеном")
    def test_upload_attachment_unauthorized(self, api_client, create_test_issue):
        issue_id = create_test_issue

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
            tmp.write(b"Test file content")
            tmp_path = tmp.name

        with open(tmp_path, "rb") as f:
            files = {"file": (os.path.basename(tmp_path), f)}
            response = api_client.upload_attachment(
                Config.INVALID_TOKEN,
                issue_id,
                files
            )
        os.unlink(tmp_path)

        assert response.status_code == 401
        validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Прикрепление файла к несуществующей задаче")
    def test_upload_attachment_nonexistent_issue(self, api_client):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
            tmp.write(b"Test file content")
            tmp_path = tmp.name

        with open(tmp_path, "rb") as f:
            files = {"file": (os.path.basename(tmp_path), f)}
            response = api_client.upload_attachment(
                Config.OAUTH_TOKEN,
                Config.INVALID_ISSUE_ID,
                files
            )
        os.unlink(tmp_path)

        assert response.status_code == 404
        validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Прикрепление файла без файла (ошибка)")
    def test_upload_attachment_without_file(self, api_client, create_test_issue):
        issue_id = create_test_issue

        response = api_client.upload_attachment(
            Config.OAUTH_TOKEN,
            issue_id,
            files={}
        )
        assert response.status_code in [400, 422]
        validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Прикрепление файла с переименованием")
    def test_upload_attachment_with_filename_param(self, api_client, create_test_issue):
        issue_id = create_test_issue

        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
            tmp.write(b"Test file content")
            tmp_path = tmp.name

        new_filename = "renamed_file.txt"
        with open(tmp_path, "rb") as f:
            files = {"file": (new_filename, f)}
            response = api_client.upload_attachment(
                Config.OAUTH_TOKEN,
                issue_id,
                files
            )
        os.unlink(tmp_path)

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == new_filename

    @allure.title("Прикрепление файла большого размера")
    def test_upload_large_attachment(self, api_client, create_test_issue):
        issue_id = create_test_issue

        with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as tmp:
            tmp.write(os.urandom(5 * 1024 * 1024))
            tmp_path = tmp.name

        with open(tmp_path, "rb") as f:
            files = {"file": (os.path.basename(tmp_path), f)}
            response = api_client.upload_attachment(
                Config.OAUTH_TOKEN,
                issue_id,
                files
            )
        os.unlink(tmp_path)

        assert response.status_code == 201
        data = response.json()
        assert data["size"] >= 5 * 1024 * 1024
