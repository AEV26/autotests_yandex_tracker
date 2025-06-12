import allure
import pytest
from utils.validators import ResponseValidator


@allure.feature("Issues")
@allure.story("Create Issue")
class TestCreateIssue:
    @allure.title("Create issue with minimal data")
    def test_create_minimal_issue(self, api_client_2, validator, minimal_issue_data):
        with allure.step("Send request to create issue"):
            response = api_client_2.create_issue(minimal_issue_data)

        with allure.step("Check response status code"):
            assert response.status_code == 201

        with allure.step("Validate response structure"):
            issue = response.json()
            validator.validate_issue_response(issue)

        with allure.step("Check response content"):
            assert issue["summary"] == minimal_issue_data["summary"]
            assert issue["queue"]["key"] == minimal_issue_data["queue"]

    @allure.title("Create issue with full data")
    def test_create_full_issue(self, api_client_2, validator, full_issue_data):
        with allure.step("Send request to create issue"):
            response = api_client_2.create_issue(full_issue_data)

        with allure.step("Check response status code"):
            assert response.status_code == 201

        with allure.step("Validate response structure"):
            issue = response.json()
            validator.validate_issue_response(issue)

        with allure.step("Check response content"):
            assert issue["summary"] == full_issue_data["summary"]
            assert issue["queue"]["key"] == full_issue_data["queue"]
            if "type" in issue:
                assert "key" in issue["type"] or "name" in issue["type"]
            if "priority" in issue:
                assert "key" in issue["priority"] or "name" in issue["priority"]

    @allure.title("Create issue without required field")
    def test_create_issue_without_summary(self, api_client_2, validator, minimal_issue_data):
        issue_data = minimal_issue_data.copy()
        issue_data.pop("summary")

        with allure.step("Send request without summary"):
            response = api_client_2.create_issue(issue_data)

        with allure.step("Check response status code"):
            assert response.status_code == 400

        with allure.step("Validate error structure"):
            error = response.json()
            validator.validate_error_response(error)

        with allure.step("Check error message"):
            assert "summary" in str(error)

    @allure.title("Create issue with invalid queue")
    def test_create_issue_with_invalid_queue(self, api_client_2, validator, minimal_issue_data):
        issue_data = minimal_issue_data.copy()
        issue_data["queue"] = "INVALID"

        with allure.step("Send request with invalid queue"):
            response = api_client_2.create_issue(issue_data)

        with allure.step("Check response status code"):
            assert response.status_code == 404

        with allure.step("Validate error structure"):
            error = response.json()
            validator.validate_error_response(error)

        with allure.step("Check error message"):
            error_message = str(error).lower()
            assert any(word in error_message for word in ["queue", "очередь"])

    @allure.title("Create issue without authorization")
    def test_create_issue_without_auth(self, api_client_2, validator, minimal_issue_data):
        with allure.step("Send request without auth token"):
            response = api_client_2.create_issue(
                minimal_issue_data,
                headers={"Authorization": None, "X-Cloud-Org-ID": None}
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

            with allure.step("Check error message"):
                assert any(phrase in error_message
                           for phrase in ["unauthorized", "authorization required", "authentication"])

    @allure.title("Create issue with invalid organization ID")
    def test_create_issue_with_invalid_org_id(self, api_client_2, validator, minimal_issue_data):
        with allure.step("Send request with invalid org ID"):
            response = api_client_2.create_issue(
                minimal_issue_data,
                headers={"X-Cloud-Org-ID": "invalid"}
            )

        with allure.step("Check response status code"):
            assert response.status_code == 403

        with allure.step("Validate error structure"):
            error = response.json()
            validator.validate_error_response(error)

        with allure.step("Check error message"):
            error_message = str(error).lower()
            assert any(word in error_message
                       for word in ["permission", "organization", "not available"])