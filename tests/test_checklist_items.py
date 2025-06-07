import allure
import pytest
from jsonschema import validate

from utils.api_client import ChecklistItem
from schemas.checklist_schema import (
    checklist_schema,
    error_schema
)


@allure.feature("Checklist API")
@allure.story("Получение чек-листа задачи")
class TestChecklistItems:
    @allure.title("Позитивный тест: получение чек-листа существующей задачи")
    def test_get_checklist_success(self, api_client):
        with allure.step("Запрашиваем чек-лист для существующей задачи"):
            response = api_client.get_checklist_items("EDU-13")

        with allure.step("Проверяем код ответа"):
            assert response.status_code == 200

        with allure.step("Валидируем структуру ответа"):
            items = response.json()
            validate(instance=items, schema=checklist_schema)

        with allure.step("Проверяем типы данных через Pydantic"):
            [ChecklistItem(**item) for item in items]

    @allure.title("Неавторизованный доступ")
    def test_unauthorized_access(self, unauthorized_client):
        with allure.step("Запрос с невалидным токеном"):
            response = unauthorized_client.get_checklist_items("EDU-13")

        with allure.step("Проверяем код 401"):
            assert response.status_code == 401

        with allure.step("Валидируем структуру ошибки"):
            validate(instance=response.json(), schema=error_schema)

    @allure.title("Запрос несуществующей задачи")
    def test_nonexistent_issue(self, api_client):
        with allure.step("Запрос чек-листа для несуществующей задачи"):
            response = api_client.get_checklist_items("NONEXISTENT-999")

        with allure.step("Проверяем код 404"):
            assert response.status_code == 404

        with allure.step("Валидируем структуру ошибки"):
            validate(instance=response.json(), schema=error_schema)

    @allure.title("Проверка пагинации")
    @pytest.mark.parametrize("per_page", [1, 5, 10])
    def test_pagination(self, api_client, per_page):
        with allure.step(f"Запрос с пагинацией (perPage={per_page})"):
            response = api_client.get_checklist_items(
                "EDU-13",
                params={"perPage": per_page}
            )

        with allure.step("Проверяем код ответа"):
            assert response.status_code == 200

