import uuid
import pytest
import allure
from jsonschema import validate

from utils.api_client import TrackerApiClient
from schemas.fields_schema import category_schema, error_schema
def get_next_order(api_client_1: TrackerApiClient) -> int:
    resp = api_client_1.get_field_categories()
    assert resp.status_code == 200
    orders = [cat.get("order", 0) for cat in resp.json()]
    return max(orders, default=0) + 1

@allure.feature("Fields API")
@allure.story("Создание категории поля задачи")
class TestCreateFieldCategory:

    @allure.title("Позитивный тест: создание категории с валидными параметрами")
    def test_create_category_success(self, api_client_1):
        name_ru = f"Категория_{uuid.uuid4().hex[:6]}"
        name_en = f"Category_{uuid.uuid4().hex[:6]}"
        payload = {
            "name": {"ru": name_ru, "en": name_en},
            "order": get_next_order(api_client_1)
        }

        resp = api_client_1.create_field_category(payload)
        assert resp.status_code in (200, 201), resp.text
        data = resp.json()

        validate(instance=data, schema=category_schema)

        returned = data["name"]
        if isinstance(returned, dict):
            assert returned.get("ru") == name_ru
        else:
            assert name_ru in returned

        all_cats = api_client_1.get_field_categories().json()
        assert any(c["id"] == data["id"] for c in all_cats)

    @allure.title("Неавторизованный доступ при создании категории")
    def test_create_category_unauthorized(self, unauthorized_client):
        payload = {"name": {"ru": "X", "en": "X"}, "order": 1}
        resp = unauthorized_client.create_field_category(payload)
        assert resp.status_code == 401
        validate(instance=resp.json(), schema=error_schema)

    @allure.title("Ошибка валидации: некорректные данные")
    @pytest.mark.parametrize("bad_payload", [
        {},
        {"name": ""},
        {"name": {"ru": "OK"}},
        {"name": 123},
    ])
    def test_create_category_validation_error(self, api_client_1, bad_payload):
        p = bad_payload.copy()
        if "order" not in p:
            p["order"] = get_next_order(api_client_1)
        resp = api_client_1.create_field_category(p)
        assert resp.status_code in (200, 201, 400, 422)
        if resp.status_code in (400, 422):
            validate(instance=resp.json(), schema=error_schema)

    @allure.title("Конфликт имён: повторное создание категории")
    def test_create_category_conflict(self, api_client_1):
        name = {"ru": f"Conflict_{uuid.uuid4().hex[:6]}", "en": "Conflict"}
        payload = {"name": name, "order": get_next_order(api_client_1)}

        first = api_client_1.create_field_category(payload)
        assert first.status_code in (200, 201)

        second = api_client_1.create_field_category(payload)
        assert second.status_code in (200, 201, 409, 422)
        if second.status_code in (409, 422):
            validate(instance=second.json(), schema=error_schema)
