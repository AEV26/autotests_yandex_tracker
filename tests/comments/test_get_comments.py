import pytest
import allure
from config import Config
from utils.validators import validate_response_schema, validate_error_response
from utils.api_client import TrackerAPIClient
from schemas.comment_list_schema import COMMENT_LIST_SCHEMA
from schemas.error_schema import ERROR_SCHEMA


@allure.feature("Яндекс.Трекер API")
@allure.story("Получение комментариев")
class TestGetComments:

    @allure.title("Позитивный сценарий: получение списка комментариев")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_comments_success(self, api_client):
        with allure.step("Отправка запроса на получение комментариев"):
            response = api_client.get_comments(
                Config.OAUTH_TOKEN,
                Config.TEST_ISSUE_ID
            )

        with allure.step("Проверка ответа"):
            assert response.status_code == 200
            validate_response_schema(response, COMMENT_LIST_SCHEMA)

            response_data = response.json()
            assert isinstance(response_data, list)
            if len(response_data) > 0:
                first_comment = response_data[0]
                assert "text" in first_comment
                assert "createdBy" in first_comment

    @allure.title("Неавторизованный доступ: невалидный токен")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_comments_unauthorized(self, api_client):
        with allure.step("Отправка запроса с невалидным токеном"):
            response = api_client.get_comments(
                Config.INVALID_TOKEN,
                Config.TEST_ISSUE_ID
            )

        with allure.step("Проверка ответа"):
            assert response.status_code == 401
            validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Несуществующая задача")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_comments_invalid_issue(self, api_client):
        with allure.step("Отправка запроса для несуществующей задачи"):
            response = api_client.get_comments(
                Config.OAUTH_TOKEN,
                Config.INVALID_ISSUE_ID
            )

        with allure.step("Проверка ответа"):
            assert response.status_code == 404
            validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Получение пустого списка комментариев")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_empty_comments(self, api_client, create_empty_issue):
        with allure.step("Отправка запроса для задачи без комментариев"):
            response = api_client.get_comments(
                Config.OAUTH_TOKEN,
                create_empty_issue["id"]
            )

        with allure.step("Проверка ответа"):
            assert response.status_code == 200
            response_data = response.json()
            assert isinstance(response_data, list)
            assert len(response_data) == 0

