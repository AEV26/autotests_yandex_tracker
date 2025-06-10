import pytest
import allure
from config import Config
from utils.validators import validate_error_response, validate_response_schema
from schemas.error_schema import ERROR_SCHEMA
from schemas.project_comments_list_schema import PROJECT_COMMENTS_LIST_SCHEMA


@allure.feature("Яндекс.Трекер API")
@allure.story("Получение комментариев проекта TESTN PROJECT")
class TestGetProjectComments:

    @allure.title("Успешное получение списка комментариев проекта")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_get_project_comments_success(self, api_client, project_with_comments):
        project_id, expected_comment_ids = project_with_comments

        with allure.step("Отправка запроса на получение комментариев проекта"):
            response = api_client.get_entity_comments(
                Config.OAUTH_TOKEN,
                "project",
                project_id
            )

        with allure.step("Проверка ответа"):
            assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}"
            validate_response_schema(response, PROJECT_COMMENTS_LIST_SCHEMA)

            comments = response.json()
            assert isinstance(comments, list), "Ответ должен быть массивом"
            assert len(comments) >= len(
                expected_comment_ids), f"Ожидалось минимум {len(expected_comment_ids)} комментариев"

            comment_ids = [comment["id"] for comment in comments]
            for expected_id in expected_comment_ids:
                assert expected_id in comment_ids, f"Комментарий {expected_id} не найден в списке"

    @allure.title("Получение комментариев проекта с невалидным токеном")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_project_comments_unauthorized(self, api_client, testn_project_id):
        with allure.step("Отправка запроса с невалидным токеном"):
            response = api_client.get_entity_comments(
                Config.INVALID_TOKEN,
                "project",
                testn_project_id
            )

        with allure.step("Проверка ответа"):
            assert response.status_code == 401
            validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Получение комментариев несуществующего проекта")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_comments_nonexistent_project(self, api_client):
        nonexistent_project_id = "nonexistent-project-id"

        with allure.step("Отправка запроса для несуществующего проекта"):
            response = api_client.get_entity_comments(
                Config.OAUTH_TOKEN,
                "project",
                nonexistent_project_id
            )

        with allure.step("Проверка ответа"):
            assert response.status_code == 400
            validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Получение комментариев проекта без токена")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_get_project_comments_no_token(self, api_client, testn_project_id):
        with allure.step("Отправка запроса без токена"):
            response = api_client.get_entity_comments(
                "",
                "project",
                testn_project_id
            )

        with allure.step("Проверка ответа"):
            assert response.status_code == 401
            validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Получение комментариев проекта без комментариев")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_empty_comments_list(self, api_client, testn_project_id):
        with allure.step("Отправка запроса для проекта"):
            response = api_client.get_entity_comments(
                Config.OAUTH_TOKEN,
                "project",
                testn_project_id
            )

        with allure.step("Проверка ответа"):
            assert response.status_code == 200
            validate_response_schema(response, PROJECT_COMMENTS_LIST_SCHEMA)

            comments = response.json()
            assert isinstance(comments, list), "Ответ должен быть массивом"

    @allure.title("Получение комментариев с невалидным типом сущности")
    @allure.severity(allure.severity_level.NORMAL)
    def test_get_comments_invalid_entity_type(self, api_client, testn_project_id):
        invalid_entity_type = "invalid_entity_type"

        with allure.step("Отправка запроса с невалидным типом сущности"):
            response = api_client.get_entity_comments(
                Config.OAUTH_TOKEN,
                invalid_entity_type,
                testn_project_id
            )

        with allure.step("Проверка ответа"):
            assert response.status_code in [400, 404]
            validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Сравнение результатов запроса списка и отдельного комментария")
    @allure.severity(allure.severity_level.NORMAL)
    def test_compare_list_and_single_comment(self, api_client, project_with_single_comment):
        project_id, comment_id, _ = project_with_single_comment

        with allure.step("Получение списка комментариев"):
            list_response = api_client.get_entity_comments(
                Config.OAUTH_TOKEN,
                "project",
                project_id
            )
            assert list_response.status_code == 200
            comments_list = list_response.json()

        with allure.step("Получение отдельного комментария"):
            single_response = api_client.get_entity_comment(
                Config.OAUTH_TOKEN,
                "project",
                project_id,
                comment_id
            )
            assert single_response.status_code == 200
            single_comment = single_response.json()

        with allure.step("Сравнение данных"):
            list_comment = None
            for comment in comments_list:
                if comment["id"] == comment_id:
                    list_comment = comment
                    break

            assert list_comment is not None, "Комментарий не найден в списке"

            assert list_comment["id"] == single_comment["id"]
            assert list_comment["text"] == single_comment["text"]
            assert list_comment["createdAt"] == single_comment["createdAt"]
