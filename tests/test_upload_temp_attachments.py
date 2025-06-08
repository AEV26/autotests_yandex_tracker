import pytest
import tempfile
import os
import allure
from config import Config
from utils.validators import validate_error_response
from schemas.error_schema import ERROR_SCHEMA

@allure.feature("Яндекс.Трекер API")
@allure.story("Загрузка временного файла")
class TestUploadTempAttachment:

    @allure.title("Успешная загрузка временного файла")
    def test_upload_temp_attachment_success(self, api_client):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
            tmp.write(b"Temporary file content")
            tmp_path = tmp.name
            file_name = os.path.basename(tmp_path)

        with open(tmp_path, "rb") as f:
            files = {"file": (file_name, f)}
            response = api_client.upload_temp_attachment(
                Config.OAUTH_TOKEN,
                files
            )
        os.unlink(tmp_path)

        assert response.status_code == 201, f"Статус: {response.status_code}, тело: {response.text}"
        data = response.json()
        assert "id" in data
        assert data["name"] == file_name

    @allure.title("Загрузка временного файла с невалидным токеном")
    def test_upload_temp_attachment_unauthorized(self, api_client):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
            tmp.write(b"Temporary file content")
            tmp_path = tmp.name

        with open(tmp_path, "rb") as f:
            files = {"file": (os.path.basename(tmp_path), f)}
            response = api_client.upload_temp_attachment(
                Config.INVALID_TOKEN,
                files
            )
        os.unlink(tmp_path)

        assert response.status_code == 401
        validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Загрузка без файла (ошибка)")
    def test_upload_temp_attachment_without_file(self, api_client):
        response = api_client.upload_temp_attachment(
            Config.OAUTH_TOKEN,
            files={}
        )
        assert response.status_code in [400, 422]
        validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Загрузка большого временного файла")
    def test_upload_temp_large_attachment(self, api_client):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as tmp:
            tmp.write(os.urandom(2 * 1024 * 1024))  # 2MB
            tmp_path = tmp.name

        with open(tmp_path, "rb") as f:
            files = {"file": (os.path.basename(tmp_path), f)}
            response = api_client.upload_temp_attachment(
                Config.OAUTH_TOKEN,
                files
            )
        os.unlink(tmp_path)

        assert response.status_code == 201
        data = response.json()
        assert data["size"] >= 2 * 1024 * 1024
