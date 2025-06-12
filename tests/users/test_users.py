import pytest
import allure
from config import Config
from utils.validators import validate_error_response
from schemas.error_schema import ERROR_SCHEMA


@allure.feature("Яндекс.Трекер API")
@allure.story("Получение информации о пользователях")
class TestGetUsers:

    @allure.title("Успешное получение списка пользователей")
    def test_get_users_success(self, api_client):
        response = api_client.get_users(Config.OAUTH_TOKEN)

        assert response.status_code == 200, f"Статус: {response.status_code}, тело: {response.text}"
        data = response.json()
        assert isinstance(data, list), "Ответ должен быть массивом"

        if data:
            user = data[0]
            required_fields = ["self", "uid", "login", "firstName", "lastName", "display", "email"]
            for field in required_fields:
                assert field in user, f"В ответе отсутствует поле: {field}"

            assert isinstance(user["uid"], int)
            assert isinstance(user["login"], str)
            assert "@" in user["email"]

    @allure.title("Получение пользователей с невалидным токеном")
    def test_get_users_unauthorized(self, api_client):
        response = api_client.get_users(Config.INVALID_TOKEN)

        assert response.status_code == 401
        validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Получение пользователей без токена")
    def test_get_users_no_token(self, api_client):
        response = api_client.get_users("")

        assert response.status_code == 401
        validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Получение пользователей с невалидным org_id")
    def test_get_users_invalid_org_id(self, api_client, monkeypatch):
        monkeypatch.setattr("config.Config.ORG_ID", "invalid-org-id")

        response = api_client.get_users(Config.OAUTH_TOKEN)

        assert response.status_code in [401, 403, 404]
        validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Получение пользователей с параметрами пагинации")
    def test_get_users_with_pagination(self, api_client):
        params = {
            "perPage": 5,
            "page": 1
        }

        response = api_client.get_users(Config.OAUTH_TOKEN, params)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5, "Количество пользователей не должно превышать perPage"

    @allure.title("Проверка структуры данных пользователя")
    def test_user_data_structure(self, api_client):
        response = api_client.get_users(Config.OAUTH_TOKEN)

        assert response.status_code == 200
        users = response.json()

        if users:
            user = users[0]

            assert "self" in user
            assert "uid" in user
            assert "login" in user
            assert "display" in user
            assert "email" in user

            assert isinstance(user["uid"], int)
            assert isinstance(user["login"], str)
            assert isinstance(user["display"], str)
            assert isinstance(user["email"], str)

            optional_fields = ["firstName", "lastName", "trackerUid", "passportUid",
                               "cloudUid", "hasLicense", "dismissed", "external"]
            for field in optional_fields:
                if field in user:
                    assert user[field] is not None

    @allure.title("Поиск конкретного пользователя в списке")
    def test_find_specific_user(self, api_client):
        response = api_client.get_users(Config.OAUTH_TOKEN)

        assert response.status_code == 200
        users = response.json()

        myself_response = api_client.get_myself(Config.OAUTH_TOKEN)
        if myself_response.status_code == 200:
            myself_data = myself_response.json()
            my_uid = myself_data["uid"]

            found_user = next((u for u in users if u["uid"] == my_uid), None)
            assert found_user is not None, "Текущий пользователь должен быть в списке пользователей"
            assert found_user["login"] == myself_data["login"]