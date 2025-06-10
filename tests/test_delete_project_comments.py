import pytest
import allure
from config import Config
from utils.validators import validate_error_response
from schemas.error_schema import ERROR_SCHEMA


@allure.feature("Яндекс.Трекер API")
@allure.story("Удаление комментариев проекта TESTN PROJECT")
class TestDeleteProjectComments:

    @allure.title("Успешное удаление комментария проекта")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_project_comment_success(self, api_client, create_comment_for_deletion):
        project_id, comment_id = create_comment_for_deletion

        with allure.step("Удаление комментария"):
            response = api_client.delete_entity_comment(
                Config.OAUTH_TOKEN,
                "project",
                project_id,
                comment_id
            )

        with allure.step("Проверка ответа"):
            assert response.status_code == 204, f"Ожидался статус 204, получен {response.status_code}"

        with allure.step("Проверка, что комментарий удален"):
            comments_response = api_client.get_entity_comments(
                Config.OAUTH_TOKEN,
                "project",
                project_id
            )
            assert comments_response.status_code == 200
            comments = comments_response.json()
            comment_ids = [comment["id"] for comment in comments]
            assert comment_id not in comment_ids, "Комментарий не был удален"

    @allure.title("Удаление комментария с невалидным токеном")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_project_comment_unauthorized(self, api_client, create_comment_for_deletion):
        project_id, comment_id = create_comment_for_deletion

        with allure.step("Отправка запроса с невалидным токеном"):
            response = api_client.delete_entity_comment(
                Config.INVALID_TOKEN,
                "project",
                project_id,
                comment_id
            )

        with allure.step("Проверка ответа"):
            assert response.status_code == 401
            validate_error_response(response, ERROR_SCHEMA)

        with allure.step("Проверка, что комментарий не удален"):
            comments_response = api_client.get_entity_comments(
                Config.OAUTH_TOKEN,
                "project",
                project_id
            )
            assert comments_response.status_code == 200
            comments = comments_response.json()
            comment_ids = [comment["id"] for comment in comments]
            assert comment_id in comment_ids, "Комментарий был удален несмотря на невалидный токен"

    @allure.title("Удаление несуществующего комментария")
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_nonexistent_comment(self, api_client, testn_project_id):
        nonexistent_comment_id = 999999999

        with allure.step("Отправка запроса для несуществующего комментария"):
            response = api_client.delete_entity_comment(
                Config.OAUTH_TOKEN,
                "project",
                testn_project_id,
                nonexistent_comment_id
            )

        with allure.step("Проверка ответа"):
            assert response.status_code == 404
            validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Удаление комментария без токена")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_project_comment_no_token(self, api_client, create_comment_for_deletion):
        project_id, comment_id = create_comment_for_deletion

        with allure.step("Отправка запроса без токена"):
            response = api_client.delete_entity_comment(
                "",
                "project",
                project_id,
                comment_id
            )

        with allure.step("Проверка ответа"):
            assert response.status_code == 401
            validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Удаление комментария из несуществующего проекта")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_delete_comment_from_nonexistent_project(self, api_client):
        nonexistent_project_id = "nonexistent-project-id"
        some_comment_id = 123

        with allure.step("Отправка запроса для несуществующего проекта"):
            response = api_client.delete_entity_comment(
                Config.OAUTH_TOKEN,
                "project",
                nonexistent_project_id,
                some_comment_id
            )

        with allure.step("Проверка ответа"):
            assert response.status_code == 400
            validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Удаление уже удаленного комментария")
    @allure.severity(allure.severity_level.MINOR)
    def test_delete_already_deleted_comment(self, api_client, create_comment_for_deletion):
        project_id, comment_id = create_comment_for_deletion

        with allure.step("Первое удаление комментария"):
            first_response = api_client.delete_entity_comment(
                Config.OAUTH_TOKEN,
                "project",
                project_id,
                comment_id
            )
            assert first_response.status_code == 204

        with allure.step("Повторное удаление того же комментария"):
            second_response = api_client.delete_entity_comment(
                Config.OAUTH_TOKEN,
                "project",
                project_id,
                comment_id
            )

        with allure.step("Проверка ответа"):
            assert second_response.status_code in [404, 410]
            validate_error_response(second_response, ERROR_SCHEMA)

    @allure.title("Массовое удаление комментариев")
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_multiple_comments(self, api_client, create_multiple_comments_for_deletion):
        project_id, comment_ids = create_multiple_comments_for_deletion

        deleted_comment_ids = []

        for comment_id in comment_ids:
            with allure.step(f"Удаление комментария {comment_id}"):
                response = api_client.delete_entity_comment(
                    Config.OAUTH_TOKEN,
                    "project",
                    project_id,
                    comment_id
                )
                assert response.status_code == 204
                deleted_comment_ids.append(comment_id)

        with allure.step("Проверка, что все комментарии удалены"):
            comments_response = api_client.get_entity_comments(
                Config.OAUTH_TOKEN,
                "project",
                project_id
            )
            assert comments_response.status_code == 200
            comments = comments_response.json()
            remaining_comment_ids = [comment["id"] for comment in comments]

            for deleted_id in deleted_comment_ids:
                assert deleted_id not in remaining_comment_ids, f"Комментарий {deleted_id} не был удален"

    @allure.title("Удаление комментария с невалидным типом сущности")
    @allure.severity(allure.severity_level.NORMAL)
    def test_delete_comment_invalid_entity_type(self, api_client, testn_project_id):
        invalid_entity_type = "invalid_entity_type"
        some_comment_id = 123

        with allure.step("Отправка запроса с невалидным типом сущности"):
            response = api_client.delete_entity_comment(
                Config.OAUTH_TOKEN,
                invalid_entity_type,
                testn_project_id,
                some_comment_id
            )

        with allure.step("Проверка ответа"):
            assert response.status_code in [400, 404]
            validate_error_response(response, ERROR_SCHEMA)
