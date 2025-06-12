import pytest
import allure
from config import Config
from utils.validators import validate_response_schema, validate_error_response
from schemas.error_schema import ERROR_SCHEMA


@allure.feature("Яндекс.Трекер API")
@allure.story("Удаление комментариев")
class TestDeleteComment:

    @allure.title("Успешное удаление комментария")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_comment_success(self, api_client, create_test_comment):
        issue_id, comment_id = create_test_comment

        with allure.step("Удаляем комментарий"):
            response = api_client.delete_comment(
                Config.OAUTH_TOKEN,
                issue_id,
                comment_id
            )

        with allure.step("Проверяем ответ"):
            assert response.status_code == 204

        with allure.step("Проверяем что комментарий удален"):
            get_response = api_client.get_comments(Config.OAUTH_TOKEN, issue_id)
            comments = get_response.json()
            assert all(comment['id'] != comment_id for comment in comments)

    @allure.title("Удаление несуществующего комментария")
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_nonexistent_comment(self, api_client, create_test_comment):
        issue_id, _ = create_test_comment
        invalid_comment_id = "999999999"

        response = api_client.delete_comment(
            Config.OAUTH_TOKEN,
            issue_id,
            invalid_comment_id
        )

        assert response.status_code == 404
        validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Удаление с невалидным токеном")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_comment_unauthorized(self, api_client, create_test_comment):
        issue_id, comment_id = create_test_comment

        response = api_client.delete_comment(
            Config.INVALID_TOKEN,
            issue_id,
            comment_id
        )

        assert response.status_code == 401
        validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Удаление уже удаленного комментария")
    @allure.severity(allure.severity_level.MINOR)
    def test_delete_already_deleted(self, api_client, create_test_comment):
        issue_id, comment_id = create_test_comment

        first_response = api_client.delete_comment(
            Config.OAUTH_TOKEN,
            issue_id,
            comment_id
        )
        assert first_response.status_code == 204

        second_response = api_client.delete_comment(
            Config.OAUTH_TOKEN,
            issue_id,
            comment_id
        )
        assert second_response.status_code in [404, 410]


    @allure.title("Удаление комментария из несуществующей задачи")
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_comment_from_nonexistent_issue(self, api_client, create_test_comment):
        _, comment_id = create_test_comment

        response = api_client.delete_comment(
            Config.OAUTH_TOKEN,
            Config.INVALID_ISSUE_ID,
            comment_id
        )

        assert response.status_code == 404
        validate_error_response(response, ERROR_SCHEMA)


    @allure.title("Удаление комментария с невалидным ID")
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_comment_with_invalid_id_format(self, api_client, create_test_comment):
        issue_id, _ = create_test_comment

        invalid_comment_ids = [
            "invalid_id",
            "123.45",
            "0",
            "-100"
        ]

        for comment_id in invalid_comment_ids:
            with allure.step(f"Проверка ID: {comment_id}"):
                response = api_client.delete_comment(
                    Config.OAUTH_TOKEN,
                    issue_id,
                    comment_id
                )
                assert response.status_code in [400, 404]
                if response.status_code == 400:
                    validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Удаление комментария без прав доступа")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_comment_without_permissions(self, api_client, create_test_comment):
        issue_id, comment_id = create_test_comment

        response = api_client.delete_comment(
            Config.INVALID_TOKEN,
            issue_id,
            comment_id
        )

        assert response.status_code == 401
        validate_error_response(response, ERROR_SCHEMA)


    @allure.title("Удаление комментария с проверкой idempotency")
    @allure.severity(allure.severity_level.MINOR)
    def test_delete_comment_idempotency(self, api_client, create_test_comment):
        issue_id, comment_id = create_test_comment
        first_response = api_client.delete_comment(
            Config.OAUTH_TOKEN,
            issue_id,
            comment_id
        )
        assert first_response.status_code == 204

        second_response = api_client.delete_comment(
            Config.OAUTH_TOKEN,
            issue_id,
            comment_id
        )
        assert second_response.status_code in [404, 410]

        get_response = api_client.get_comments(Config.OAUTH_TOKEN, issue_id)
        comments = get_response.json()
        assert all(comment['id'] != comment_id for comment in comments)


    @allure.title("Удаление комментария с длинным ID")
    @allure.severity(allure.severity_level.MINOR)
    def test_delete_comment_with_long_id(self, api_client):
        long_comment_id = "1" * 100

        response = api_client.delete_comment(
            Config.OAUTH_TOKEN,
            Config.TEST_ISSUE_ID,
            long_comment_id
        )

        assert response.status_code in [400, 404]
        if response.status_code == 400:
            validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Удаление комментария с пустым ID")
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_comment_with_empty_id(self, api_client, create_test_comment):
        issue_id, _ = create_test_comment

        response = api_client.delete_comment(
            Config.OAUTH_TOKEN,
            issue_id,
            ""
        )

        assert response.status_code == 405
        validate_error_response(response, ERROR_SCHEMA)