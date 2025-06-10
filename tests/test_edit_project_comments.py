import pytest
import allure
from config import Config
from utils.validators import validate_error_response, validate_response_schema
from schemas.error_schema import ERROR_SCHEMA
from schemas.updated_comment_schema import UPDATED_COMMENT_SCHEMA


@allure.feature("Яндекс.Трекер API")
@allure.story("Редактирование комментариев к проекту TESTN PROJECT")
class TestEditProjectComments:

    @allure.title("Успешное редактирование комментария к проекту")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_edit_project_comment_success(self, api_client, create_project_comment_for_editing, updated_comment_data):
        project_id, comment_id, original_comment = create_project_comment_for_editing

        with allure.step("Отправка запроса на редактирование комментария"):
            response = api_client.update_entity_comment(
                Config.OAUTH_TOKEN,
                "project",
                project_id,
                comment_id,
                updated_comment_data
            )

        with allure.step("Проверка ответа"):
            assert response.status_code in [200, 201], f"Ожидался статус 200 или 201, получен {response.status_code}"
            validate_response_schema(response, UPDATED_COMMENT_SCHEMA)

            response_data = response.json()
            assert response_data["text"] == updated_comment_data["text"]
            assert response_data["id"] == comment_id
            assert "updatedBy" in response_data
            assert "updatedAt" in response_data
            assert response_data["updatedAt"] != response_data["createdAt"]

    @allure.title("Редактирование комментария с невалидным токеном")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_edit_project_comment_unauthorized(self, api_client, create_project_comment_for_editing,
                                               updated_comment_data):
        project_id, comment_id, _ = create_project_comment_for_editing

        with allure.step("Отправка запроса с невалидным токеном"):
            response = api_client.update_entity_comment(
                Config.INVALID_TOKEN,
                "project",
                project_id,
                comment_id,
                updated_comment_data
            )

        with allure.step("Проверка ответа"):
            assert response.status_code == 401
            validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Редактирование несуществующего комментария")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_edit_nonexistent_comment(self, api_client, testn_project_id, updated_comment_data):
        nonexistent_comment_id = 999999999

        with allure.step("Отправка запроса для несуществующего комментария"):
            response = api_client.update_entity_comment(
                Config.OAUTH_TOKEN,
                "project",
                testn_project_id,
                nonexistent_comment_id,
                updated_comment_data
            )

        with allure.step("Проверка ответа"):
            assert response.status_code == 404
            validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Редактирование комментария с пустым текстом")
    @allure.severity(allure.severity_level.NORMAL)
    def test_edit_comment_empty_text(self, api_client, create_project_comment_for_editing):
        project_id, comment_id, _ = create_project_comment_for_editing
        empty_data = {"text": ""}

        with allure.step("Отправка запроса с пустым текстом"):
            response = api_client.update_entity_comment(
                Config.OAUTH_TOKEN,
                "project",
                project_id,
                comment_id,
                empty_data
            )

        with allure.step("Проверка ответа"):
            assert response.status_code in [200, 201, 400, 422]
            if response.status_code in [200, 201]:
                validate_response_schema(response, UPDATED_COMMENT_SCHEMA)
            else:
                validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Редактирование комментария с HTML-тегами")
    @allure.severity(allure.severity_level.NORMAL)
    def test_edit_comment_with_html(self, api_client, create_project_comment_for_editing):
        project_id, comment_id, _ = create_project_comment_for_editing
        html_data = {
            "text": "<b>Обновленный</b> комментарий к проекту TESTN <script>alert('test')</script>"
        }

        with allure.step("Отправка запроса с HTML-тегами"):
            response = api_client.update_entity_comment(
                Config.OAUTH_TOKEN,
                "project",
                project_id,
                comment_id,
                html_data
            )

        with allure.step("Проверка ответа"):
            assert response.status_code in [200, 201]
            validate_response_schema(response, UPDATED_COMMENT_SCHEMA)
            response_data = response.json()
            assert response_data["text"] == html_data["text"]

    @allure.title("Редактирование комментария с добавлением упоминаний")
    @allure.severity(allure.severity_level.NORMAL)
    def test_edit_comment_add_summonees(self, api_client, create_project_comment_for_editing):
        project_id, comment_id, _ = create_project_comment_for_editing
        data_with_summonees = {
            "text": "Обновленный комментарий с упоминаниями",
            "summonees": ["user1", "user2"]
        }

        with allure.step("Отправка запроса с добавлением упоминаний"):
            response = api_client.update_entity_comment(
                Config.OAUTH_TOKEN,
                "project",
                project_id,
                comment_id,
                data_with_summonees
            )

        with allure.step("Проверка ответа"):
            assert response.status_code in [200, 201, 400, 422]
            if response.status_code in [200, 201]:
                validate_response_schema(response, UPDATED_COMMENT_SCHEMA)
                response_data = response.json()
                assert response_data["text"] == data_with_summonees["text"]
            else:
                validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Редактирование комментария с длинным текстом")
    @allure.severity(allure.severity_level.NORMAL)
    def test_edit_comment_long_text(self, api_client, create_project_comment_for_editing):
        project_id, comment_id, _ = create_project_comment_for_editing
        long_text_data = {"text": "Очень длинный обновленный комментарий: " + "a" * 5000}

        with allure.step("Отправка запроса с длинным текстом"):
            response = api_client.update_entity_comment(
                Config.OAUTH_TOKEN,
                "project",
                project_id,
                comment_id,
                long_text_data
            )

        with allure.step("Проверка ответа"):
            assert response.status_code in [200, 201, 400, 422]
            if response.status_code in [200, 201]:
                validate_response_schema(response, UPDATED_COMMENT_SCHEMA)
                assert response.json()["text"] == long_text_data["text"]
            else:
                validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Редактирование комментария несуществующего проекта")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_edit_comment_nonexistent_project(self, api_client, updated_comment_data):
        nonexistent_project_id = "nonexistent-project-id"
        some_comment_id = 123

        with allure.step("Отправка запроса для несуществующего проекта"):
            response = api_client.update_entity_comment(
                Config.OAUTH_TOKEN,
                "project",
                nonexistent_project_id,
                some_comment_id,
                updated_comment_data
            )

        with allure.step("Проверка ответа"):
            assert response.status_code in [400, 404, 422]
            validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Редактирование комментария без токена")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_edit_comment_no_token(self, api_client, create_project_comment_for_editing, updated_comment_data):
        project_id, comment_id, _ = create_project_comment_for_editing

        with allure.step("Отправка запроса без токена"):
            response = api_client.update_entity_comment(
                "",
                "project",
                project_id,
                comment_id,
                updated_comment_data
            )

        with allure.step("Проверка ответа"):
            assert response.status_code == 401
            validate_error_response(response, ERROR_SCHEMA)

    @allure.title("Проверка, что комментарий действительно обновился")
    @allure.severity(allure.severity_level.NORMAL)
    def test_verify_comment_updated(self, api_client, create_project_comment_for_editing, updated_comment_data):
        project_id, comment_id, original_comment = create_project_comment_for_editing

        with allure.step("Редактирование комментария"):
            update_response = api_client.update_entity_comment(
                Config.OAUTH_TOKEN,
                "project",
                project_id,
                comment_id,
                updated_comment_data
            )
            assert update_response.status_code in [200, 201]

        with allure.step("Получение обновленного комментария"):
            get_response = api_client.get_entity_comment(
                Config.OAUTH_TOKEN,
                "project",
                project_id,
                comment_id
            )

        with allure.step("Проверка, что комментарий обновился"):
            assert get_response.status_code == 200
            updated_comment = get_response.json()
            assert updated_comment["text"] == updated_comment_data["text"]
            assert updated_comment["text"] != original_comment["text"]
            assert "updatedAt" in updated_comment
            assert updated_comment["updatedAt"] != updated_comment["createdAt"]
