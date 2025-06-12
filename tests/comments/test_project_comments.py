import pytest
import allure
from config import Config
from utils.validators import validate_error_response, validate_response_schema
from schemas.error_schema import ERROR_SCHEMA
from schemas.project_comment_schema import PROJECT_COMMENT_SCHEMA


@allure.feature("Яндекс.Трекер API")
@allure.story("Добавление комментариев к проекту TESTN PROJECT")
class TestProjectComments:

    @allure.title("Успешное добавление комментария к проекту")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_add_project_comment_success(self, api_client, testn_project_id, valid_project_comment_data):
        with allure.step("Отправка запроса на добавление комментария к проекту"):
            response = api_client.add_entity_comment(
                Config.OAUTH_TOKEN,
                "project",
                testn_project_id,
                valid_project_comment_data
            )

        with allure.step("Проверка ответа"):
            assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
            validate_response_schema(response, PROJECT_COMMENT_SCHEMA)

            response_data = response.json()
            assert response_data["text"] == valid_project_comment_data["text"]
            assert "createdBy" in response_data
            assert "createdAt" in response_data

    @allure.title("Добавление комментария к проекту с невалидным токеном")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_project_comment_unauthorized(self, api_client, testn_project_id, valid_project_comment_data):
        with allure.step("Отправка запроса с невалидным токеном"):
            response = api_client.add_entity_comment(
                Config.INVALID_TOKEN,
                "project",
                testn_project_id,
                valid_project_comment_data
            )

        with allure.step("Проверка ответа"):
            assert response.status_code == 401
            validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Добавление пустого комментария к проекту")
    @allure.severity(allure.severity_level.NORMAL)
    def test_add_empty_project_comment(self, api_client, testn_project_id):
        empty_comment_data = {"text": ""}

        with allure.step("Отправка запроса с пустым комментарием"):
            response = api_client.add_entity_comment(
                Config.OAUTH_TOKEN,
                "project",
                testn_project_id,
                empty_comment_data
            )

        with allure.step("Проверка ответа"):
            assert response.status_code in [200, 201, 400, 422]
            if response.status_code == 200:
                validate_response_schema(response, PROJECT_COMMENT_SCHEMA)
            else:
                validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Добавление комментария с упоминанием пользователей")
    @allure.severity(allure.severity_level.NORMAL)
    def test_add_comment_with_summonees(self, api_client, testn_project_id):
        comment_with_summonees = {
            "text": "Комментарий с упоминанием к проекту TESTN",
            "summonees": ["user1", "user2"]
        }

        with allure.step("Отправка запроса с упоминанием пользователей"):
            response = api_client.add_entity_comment(
                Config.OAUTH_TOKEN,
                "project",
                testn_project_id,
                comment_with_summonees
            )

        with allure.step("Проверка ответа"):
            assert response.status_code in [200, 201, 400, 422]
            if response.status_code == 200:
                validate_response_schema(response, PROJECT_COMMENT_SCHEMA)
                response_data = response.json()
                assert response_data["text"] == comment_with_summonees["text"]
            else:
                validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Добавление длинного комментария к проекту")
    @allure.severity(allure.severity_level.NORMAL)
    def test_add_long_project_comment(self, api_client, testn_project_id):
        long_comment_data = {"text": "Длинный комментарий к проекту TESTN: " + "a" * 5000}

        with allure.step("Отправка запроса с длинным комментарием"):
            response = api_client.add_entity_comment(
                Config.OAUTH_TOKEN,
                "project",
                testn_project_id,
                long_comment_data
            )

        with allure.step("Проверка ответа"):
            assert response.status_code in [200, 201, 400, 422]
            if response.status_code == 200:
                validate_response_schema(response, PROJECT_COMMENT_SCHEMA)
                assert response.json()["text"] == long_comment_data["text"]
            else:
                validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Добавление комментария с HTML-тегами")
    @allure.severity(allure.severity_level.NORMAL)
    def test_add_comment_with_html(self, api_client, testn_project_id):
        html_comment_data = {
            "text": "<b>Важный</b> комментарий к проекту TESTN <script>alert('test')</script>"
        }

        with allure.step("Отправка запроса с HTML-тегами"):
            response = api_client.add_entity_comment(
                Config.OAUTH_TOKEN,
                "project",
                testn_project_id,
                html_comment_data
            )

        with allure.step("Проверка ответа"):
            assert response.status_code == 200
            validate_response_schema(response, PROJECT_COMMENT_SCHEMA)
            response_data = response.json()
            assert response_data["text"] == html_comment_data["text"]

    @allure.title("Добавление комментария с некорректным типом данных")
    @allure.severity(allure.severity_level.NORMAL)
    def test_add_comment_invalid_data_types(self, api_client, testn_project_id):
        invalid_comment_data = {
            "text": 12345,
            "summonees": "invalid_type"
        }

        with allure.step("Отправка запроса с некорректными типами данных"):
            response = api_client.add_entity_comment(
                Config.OAUTH_TOKEN,
                "project",
                testn_project_id,
                invalid_comment_data
            )

        with allure.step("Проверка ответа"):
            assert response.status_code in [200, 201, 400, 422]
            if response.status_code in [400, 422]:
                validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Добавление комментария к несуществующему проекту")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_comment_to_nonexistent_project(self, api_client, valid_project_comment_data):
        nonexistent_project_id = "nonexistent-project-id"

        with allure.step("Отправка запроса для несуществующего проекта"):
            response = api_client.add_entity_comment(
                Config.OAUTH_TOKEN,
                "project",
                nonexistent_project_id,
                valid_project_comment_data
            )

        with allure.step("Проверка ответа"):
            assert response.status_code in [400, 404, 422]
            validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Добавление комментария без токена")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_project_comment_no_token(self, api_client, testn_project_id, valid_project_comment_data):
        with allure.step("Отправка запроса без токена"):
            response = api_client.add_entity_comment(
                "",
                "project",
                testn_project_id,
                valid_project_comment_data
            )

        with allure.step("Проверка ответа"):
            assert response.status_code == 401
            validate_error_response(response, ERROR_SCHEMA)
