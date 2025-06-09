import pytest
import allure
from config import Config
from utils.validators import validate_error_response
from schemas.error_schema import ERROR_SCHEMA


@allure.feature("Яндекс.Трекер API")
@allure.story("Получение информации о пользователе")
class TestGetUser:

    @allure.title("Успешное получение информации о пользователе по логину")
    def test_get_user_by_login_success(self, api_client, current_user_info):
        user_login = current_user_info["login"]

        response = api_client.get_user(Config.OAUTH_TOKEN, user_login)

        assert response.status_code == 200, f"Статус: {response.status_code}, тело: {response.text}"
        data = response.json()

        required_fields = ["self", "uid", "login", "firstName", "lastName", "display", "email"]
        for field in required_fields:
            assert field in data, f"В ответе отсутствует поле: {field}"

        assert data["login"] == user_login
        assert isinstance(data["uid"], int)
        assert "@" in data["email"]

    @allure.title("Успешное получение информации о пользователе по UID")
    def test_get_user_by_uid_success(self, api_client, current_user_info):
        user_uid = current_user_info["uid"]

        response = api_client.get_user(Config.OAUTH_TOKEN, str(user_uid))

        assert response.status_code == 200
        data = response.json()
        assert data["uid"] == user_uid
        assert data["login"] == current_user_info["login"]

    @allure.title("Получение информации о пользователе с невалидным токеном")
    def test_get_user_unauthorized(self, api_client, current_user_info):
        user_login = current_user_info["login"]

        response = api_client.get_user(Config.INVALID_TOKEN, user_login)

        assert response.status_code == 401
        validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Получение информации о пользователе без токена")
    def test_get_user_no_token(self, api_client, current_user_info):
        user_login = current_user_info["login"]

        response = api_client.get_user("", user_login)

        assert response.status_code == 401
        validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Получение информации о несуществующем пользователе")
    def test_get_nonexistent_user(self, api_client):
        nonexistent_user = "nonexistent_user_12345"

        response = api_client.get_user(Config.OAUTH_TOKEN, nonexistent_user)

        assert response.status_code == 404
        validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Получение пользователя с цифровым логином (специальный формат)")
    def test_get_user_numeric_login(self, api_client):
        numeric_login = "login:12345"

        response = api_client.get_user(Config.OAUTH_TOKEN, numeric_login)

        assert response.status_code in [200, 404]
        if response.status_code == 404:
            validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Получение информации о пользователе с невалидным org_id")
    def test_get_user_invalid_org_id(self, api_client, current_user_info, monkeypatch):
        user_login = current_user_info["login"]

        monkeypatch.setattr("config.Config.ORG_ID", "invalid-org-id")

        response = api_client.get_user(Config.OAUTH_TOKEN, user_login)

        assert response.status_code in [401, 403, 404]
        validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Проверка полной структуры данных пользователя")
    def test_user_data_structure_validation(self, api_client, current_user_info):
        user_login = current_user_info["login"]

        response = api_client.get_user(Config.OAUTH_TOKEN, user_login)

        assert response.status_code == 200
        data = response.json()

        assert "self" in data and data["self"].startswith("https://api.tracker.yandex.net")
        assert "uid" in data and isinstance(data["uid"], int)
        assert "login" in data and isinstance(data["login"], str)
        assert "display" in data and isinstance(data["display"], str)
        assert "email" in data and isinstance(data["email"], str)

        optional_fields = {
            "trackerUid": int,
            "passportUid": int,
            "cloudUid": str,
            "firstName": str,
            "lastName": str,
            "external": bool,
            "hasLicense": bool,
            "dismissed": bool,
            "firstLoginDate": str,
            "lastLoginDate": str,
            "welcomeMailSent": bool
        }

        for field, expected_type in optional_fields.items():
            if field in data:
                assert isinstance(data[field], expected_type), f"Поле {field} имеет неверный тип"