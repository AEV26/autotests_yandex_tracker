import pytest
import allure
from datetime import datetime
from config import Config
from utils.validators import validate_response_schema, validate_error_response
from schemas.comment_schema import COMMENT_SCHEMA
from schemas.error_schema import ERROR_SCHEMA


@allure.feature("Яндекс.Трекер API")
@allure.story("Редактирование комментариев")
class TestUpdateComment:

    @allure.title("Позитивный сценарий: обновление комментария")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_update_comment_success(self, api_client, create_test_comment):
        issue_id, comment_id = create_test_comment
        new_text = f"Updated comment {datetime.now().strftime('%Y%m%d%H%M%S')}"

        with allure.step("Отправка запроса на обновление"):
            response = api_client.update_comment(
                Config.OAUTH_TOKEN,
                issue_id,
                comment_id,
                {"text": new_text}
            )

        with allure.step("Проверка ответа"):
            assert response.status_code == 200
            validate_response_schema(response, COMMENT_SCHEMA)
            assert response.json()["text"] == new_text

    @allure.title("Обновление несуществующего комментария")
    @allure.severity(allure.severity_level.NORMAL)
    def test_update_nonexistent_comment(self, api_client, create_test_comment):
        issue_id, _ = create_test_comment
        invalid_comment_id = "999999"

        response = api_client.update_comment(
            Config.OAUTH_TOKEN,
            issue_id,
            invalid_comment_id,
            {"text": "Invalid update"}
        )

        assert response.status_code == 404
        validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Обновление с невалидным токеном")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_update_comment_unauthorized(self, api_client, create_test_comment):
        issue_id, comment_id = create_test_comment

        response = api_client.update_comment(
            Config.INVALID_TOKEN,
            issue_id,
            comment_id,
            {"text": "Unauthorized update"}
        )

        assert response.status_code == 401
        validate_error_response(response, ERROR_SCHEMA)