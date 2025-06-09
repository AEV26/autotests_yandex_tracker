import pytest
import allure
from config import Config
from utils.validators import validate_error_response
from schemas.error_schema import ERROR_SCHEMA

@allure.feature("Яндекс.Трекер API")
@allure.story("Получение информации о текущем пользователе")
class TestMyself:

    @allure.title("Успешное получение информации о себе")
    def test_get_myself_success(self, api_client):
        response = api_client.get_myself(Config.OAUTH_TOKEN)
        assert response.status_code == 200, f"Статус: {response.status_code}, тело: {response.text}"
        data = response.json()
        for key in ["self", "uid", "login", "firstName", "lastName", "display", "email"]:
            assert key in data, f"В ответе отсутствует ключ: {key}"
        assert isinstance(data["uid"], int)
        assert isinstance(data["login"], str)
        assert "@" in data["email"]

    @allure.title("Ошибка авторизации при невалидном токене")
    def test_get_myself_unauthorized(self, api_client):
        response = api_client.get_myself(Config.INVALID_TOKEN)
        assert response.status_code == 401
        validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Ошибка при отсутствии токена")
    def test_get_myself_no_token(self, api_client):
        response = api_client.get_myself("")
        assert response.status_code == 401
        validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Ошибка при невалидном org id")
    def test_get_myself_invalid_org_id(self, api_client, monkeypatch):
        monkeypatch.setattr("config.Config.ORG_ID", "invalid-org-id")
        response = api_client.get_myself(Config.OAUTH_TOKEN)
        assert response.status_code in [401, 403, 404]
        validate_error_response(response, ERROR_SCHEMA)