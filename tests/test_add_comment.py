import pytest
import allure
from config import Config
from utils.validators import validate_response_schema, validate_error_response
from schemas.comment_schema import COMMENT_SCHEMA
from schemas.error_schema import ERROR_SCHEMA


@allure.feature("Яндекс.Трекер API")
@allure.story("Добавление комментариев")
class TestAddComment:

    @allure.title("Позитивный сценарий: добавление комментария с валидными данными")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_add_comment_success(self, api_client, valid_comment_data):
        with allure.step("Отправка запроса на добавление комментария"):
            response = api_client.add_comment(
                Config.OAUTH_TOKEN,
                Config.TEST_ISSUE_ID,
                valid_comment_data
            )

        with allure.step("Проверка ответа"):
            assert response.status_code == 201
            validate_response_schema(response, COMMENT_SCHEMA)

            response_data = response.json()
            assert response_data["text"] == valid_comment_data["text"]

    @allure.title("Неавторизованный доступ: невалидный токен")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_comment_unauthorized(self, api_client, valid_comment_data):
        with allure.step("Отправка запроса с невалидным токеном"):
            response = api_client.add_comment(
                Config.INVALID_TOKEN,
                Config.TEST_ISSUE_ID,
                valid_comment_data
            )

        with allure.step("Проверка ответа"):
            assert response.status_code == 401
            validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Ошибка валидации: неверный формат комментария")
    @allure.severity(allure.severity_level.NORMAL)
    def test_add_comment_validation_error(self, api_client):
        invalid_comment_data = {
            "text": 12345,
            "summonees": "invalid_type"
        }

        response = api_client.add_comment(
            Config.OAUTH_TOKEN,
            Config.TEST_ISSUE_ID,
            invalid_comment_data
        )

        assert response.status_code in [201, 400], \
            f"Ожидался 201 или 400, получен {response.status_code}"

        if response.status_code == 400:
            validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Несуществующая задача")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_add_comment_invalid_issue(self, api_client, valid_comment_data):
        with allure.step("Отправка запроса для несуществующей задачи"):
            response = api_client.add_comment(
                Config.OAUTH_TOKEN,
                Config.INVALID_ISSUE_ID,
                valid_comment_data
            )

        with allure.step("Проверка ответа"):
            assert response.status_code == 404
            validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Добавление пустого комментария")
    @allure.severity(allure.severity_level.NORMAL)
    def test_add_empty_comment(self, api_client):
        empty_comment_data = {"text": ""}

        with allure.step("Отправка запроса с пустым комментарием"):
            response = api_client.add_comment(
                Config.OAUTH_TOKEN,
                Config.TEST_ISSUE_ID,
                empty_comment_data
            )

        with allure.step("Проверка ответа"):
            assert response.status_code in [201, 400]
            if response.status_code == 201:
                validate_response_schema(response, COMMENT_SCHEMA)
            else:
                validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Добавление очень длинного комментария")
    @allure.severity(allure.severity_level.NORMAL)
    def test_add_long_comment(self, api_client):
        long_comment_data = {"text": "a" * 10000}

        with allure.step("Отправка запроса с длинным комментарием"):
            response = api_client.add_comment(
                Config.OAUTH_TOKEN,
                Config.TEST_ISSUE_ID,
                long_comment_data
            )

        with allure.step("Проверка ответа"):
            assert response.status_code in [201, 400]
            if response.status_code == 201:
                validate_response_schema(response, COMMENT_SCHEMA)
                assert response.json()["text"] == long_comment_data["text"]
            else:
                validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Добавление комментария с HTML/XML тегами")
    @allure.severity(allure.severity_level.NORMAL)
    def test_add_comment_with_html_tags(self, api_client):
        html_comment_data = {
            "text": "<b>Важный</b> комментарий <script>alert('xss')</script>"
        }

        with allure.step("Отправка запроса с комментарием, содержащим HTML/XML теги"):
            response = api_client.add_comment(
                Config.OAUTH_TOKEN,
                Config.TEST_ISSUE_ID,
                html_comment_data
            )

        with allure.step("Проверка ответа"):
            assert response.status_code == 201
            validate_response_schema(response, COMMENT_SCHEMA)
            response_data = response.json()
            assert response_data["text"] == html_comment_data["text"]

    @allure.title("Добавление комментария с несуществующим упоминанием")
    @allure.severity(allure.severity_level.NORMAL)
    def test_add_comment_with_invalid_summonee(self, api_client):
        comment_with_invalid_summonee = {
            "text": "Комментарий с невалидным упоминанием",
            "summonees": ["nonexistent_user"]
        }

        with allure.step("Отправка запроса с невалидным упоминанием"):
            response = api_client.add_comment(
                Config.OAUTH_TOKEN,
                Config.TEST_ISSUE_ID,
                comment_with_invalid_summonee
            )

        with allure.step("Проверка ответа"):
            assert response.status_code in [201, 400]
            if response.status_code == 201:
                validate_response_schema(response, COMMENT_SCHEMA)
            else:
                validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Повторное добавление одинакового комментария")
    @allure.severity(allure.severity_level.MINOR)
    def test_add_duplicate_comment(self, api_client, valid_comment_data):
        with allure.step("Первая отправка комментария"):
            first_response = api_client.add_comment(
                Config.OAUTH_TOKEN,
                Config.TEST_ISSUE_ID,
                valid_comment_data
            )
            assert first_response.status_code == 201

        with allure.step("Вторая отправка того же комментария"):
            second_response = api_client.add_comment(
                Config.OAUTH_TOKEN,
                Config.TEST_ISSUE_ID,
                valid_comment_data
            )

        with allure.step("Проверка ответа"):
            assert second_response.status_code in [201, 400]
            if second_response.status_code == 201:
                validate_response_schema(second_response, COMMENT_SCHEMA)
            else:
                validate_error_response(second_response, ERROR_SCHEMA)