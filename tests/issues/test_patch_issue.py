import allure
import pytest
from utils.validators import ResponseValidator


@allure.feature("Issues")
@allure.story("Patch Issue")
class TestPatchIssue:
    @allure.title("Update issue summary")
    def test_patch_issue_summary(self, api_client_2, validator, created_issue):
        issue_id = created_issue["id"]
        new_summary = "Updated summary via PATCH"

        with allure.step("Send PATCH request to update summary"):
            payload = {"summary": new_summary}
            response = api_client_2.patch_issue(issue_id, payload)

        with allure.step("Check response status code"):
            assert response.status_code == 200

        with allure.step("Validate response structure"):
            issue = response.json()
            validator.validate_issue_response(issue)

        with allure.step("Check update was applied"):
            assert issue["summary"] == new_summary
            assert issue["version"] == created_issue["version"] + 1

    @allure.title("Update multiple fields")
    def test_patch_multiple_fields(self, api_client_2, validator, created_issue):
        issue_id = created_issue["id"]

        with allure.step("Send PATCH request with multiple fields"):
            payload = {
                "description": "Updated description",
                "priority": {"key": "critical"}
            }
            response = api_client_2.patch_issue(issue_id, payload)

        with allure.step("Check response status code"):
            assert response.status_code == 200

        with allure.step("Validate response structure"):
            issue = response.json()
            validator.validate_issue_response(issue)

        with allure.step("Check updates were applied"):
            assert issue["description"] == payload["description"]
            assert issue["priority"]["key"] == payload["priority"]["key"]

    @allure.title("Update non-existent issue")
    def test_patch_nonexistent_issue(self, api_client_2, validator):
        non_existent_id = "1234567890abcdef12345678"

        with allure.step("Send PATCH request to non-existent issue"):
            payload = {"summary": "Should fail"}
            response = api_client_2.patch_issue(non_existent_id, payload)

        with allure.step("Check response status code"):
            assert response.status_code == 404

        with allure.step("Validate error structure"):
            error = response.json()
            validator.validate_error_response(error)

        with allure.step("Check error message"):
            assert "задача не существует." in str(error).lower()

    @allure.title("Update issue with invalid data")
    def test_patch_invalid_data(self, api_client_2, validator, created_issue):
        issue_id = created_issue["id"]

        with allure.step("Send PATCH request with invalid priority"):
            payload = {"priority": "high"}
            response = api_client_2.patch_issue(issue_id, payload)

        with allure.step("Check response status code"):
            assert response.status_code == 422

        with allure.step("Validate error structure"):
            error = response.json()
            validator.validate_error_response(error)

        with allure.step("Check error message"):
            assert "priority" in str(error).lower()

    @allure.title("Update issue without authorization")
    def test_patch_unauthorized(self, api_client_2, validator, created_issue):
        issue_id = created_issue["id"]

        with allure.step("Send PATCH request without auth"):
            payload = {"summary": "Unauthorized update"}
            response = api_client_2.patch_issue(
                issue_id,
                payload,
                headers={"Authorization": None}
            )

        with allure.step("Check response status code"):
            assert response.status_code == 401

        with allure.step("Validate error structure"):
            try:
                error = response.json()
                validator.validate_error_response(error)
                error_message = str(error).lower()
            except ValueError:
                error_message = response.text.lower()

            assert any(phrase in error_message
                       for phrase in ["unauthorized", "authorization required"])