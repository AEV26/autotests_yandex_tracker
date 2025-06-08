import pytest
from datetime import datetime
import uuid
import time
import requests
from utils.api_client import TrackerAPIClient
from config import Config
import tempfile
import os
import hashlib
from PIL import Image
import io

@pytest.fixture
def api_client():
    return TrackerAPIClient()

@pytest.fixture
def valid_comment_data():
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return {
        "text": f"Test comment {timestamp}",
        "summonees": []
    }


@pytest.fixture
def create_empty_issue(api_client):
    issue_data = {
        "summary": "Test issue for empty comments",
        "queue": {"key": Config.QUEUE_KEY},
        "type": "task"
    }

    response = api_client.create_issue(
        Config.OAUTH_TOKEN,
        issue_data
    )
    assert response.status_code == 201
    issue = response.json()

    yield issue

    api_client.delete_issue(
        Config.OAUTH_TOKEN,
        issue["id"]
    )


@pytest.fixture
def create_test_comment(api_client):
    issue_data = {
        "summary": f"Test issue for comments {datetime.now().strftime('%H%M%S')}",
        "queue": {"key": Config.QUEUE_KEY},
        "type": "task"
    }
    issue_resp = api_client.create_issue(Config.OAUTH_TOKEN, issue_data)
    issue_id = issue_resp.json()["id"]

    comment_resp = api_client.add_comment(
        Config.OAUTH_TOKEN,
        issue_id,
        {"text": "Comment to be deleted"}
    )

    comment_data = comment_resp.json()
    comment_id = str(comment_data.get("id") or comment_data.get("longId"))

    yield issue_id, comment_id

    api_client.delete_issue(Config.OAUTH_TOKEN, issue_id)


@pytest.fixture
def create_test_issue(api_client):
    issue_data = {
        "summary": f"Test issue {datetime.now().strftime('%H%M%S')}",
        "queue": {"key": Config.QUEUE_KEY},
        "type": "task"
    }
    issue = api_client.create_issue(Config.OAUTH_TOKEN, issue_data).json()
    yield issue["id"]
    api_client.delete_issue(Config.OAUTH_TOKEN, issue["id"])


@pytest.fixture
def issue_with_attachments(api_client):
    issue_data = {
        "summary": "Issue with real attachments",
        "queue": {"key": Config.QUEUE_KEY},
        "type": "task"
    }
    issue = api_client.create_issue(Config.OAUTH_TOKEN, issue_data).json()
    issue_id = issue["id"]

    test_files = []
    for i in range(2):
        with tempfile.NamedTemporaryFile(suffix=f"_test_{i}.txt", delete=False) as tmp:
            tmp.write(f"Test file content {i}".encode())
            tmp_path = tmp.name

        with open(tmp_path, 'rb') as f:
            upload_response = requests.post(
                f"{Config.TRACKER_API_URL}/issues/{issue_id}/attachments",
                headers={
                    "Authorization": f"OAuth {Config.OAUTH_TOKEN}",
                    "X-Cloud-Org-ID": Config.ORG_ID
                },
                files={'file': f}
            )
            upload_response.raise_for_status()
            test_files.append(upload_response.json()["name"])

        os.unlink(tmp_path)

    yield issue_id, test_files

    api_client.delete_issue(Config.OAUTH_TOKEN, issue_id)


@pytest.fixture
def create_issue_with_multiple_comments(api_client):
    issue = api_client.create_issue(...)
    for i in range(3):
        api_client.add_comment(Config.OAUTH_TOKEN, issue["id"], {"text": f"Test comment {i}"})
    yield issue["id"]
    api_client.delete_issue(Config.OAUTH_TOKEN, issue["id"])


@pytest.fixture
def create_test_comment_with_author(api_client):
    issue = api_client.create_issue(...)
    comment = api_client.add_comment(
        Config.TEST_USER_TOKEN,
        issue["id"],
        {"text": "Comment from test user"}
    )
    yield issue["id"], comment.json()["createdBy"]
    api_client.delete_issue(Config.OAUTH_TOKEN, issue["id"])


@pytest.fixture
def test_file():
    file_path = "test_file.txt"
    with open(file_path, "w") as f:
        f.write("Test content")
    yield file_path

    if os.path.exists(file_path):
        os.remove(file_path)


@pytest.fixture
def create_issue_with_attachment(api_client, test_file):
    issue_data = {
        "queue": {"key": Config.QUEUE_KEY},
        "summary": "Test issue with attachment",
        "description": "Test description",
        "type": "task"
    }
    issue_response = api_client.create_issue(Config.OAUTH_TOKEN, issue_data)
    assert issue_response.status_code == 201, f"Фактический ответ: {issue_response.text}"
    issue = issue_response.json()

    with open(test_file, "rb") as f:
        files = {"file": f}
        upload_response = api_client.upload_attachment(
            Config.OAUTH_TOKEN,
            issue["id"],
            files
        )
    assert upload_response.status_code == 201
    attachment = upload_response.json()
    attachment_id = attachment["id"]
    attachment_name = attachment["name"]

    get_response = api_client.get_attachments(Config.OAUTH_TOKEN, issue["id"])
    assert get_response.status_code == 200
    attachments = get_response.json()
    assert any(att["id"] == attachment["id"] for att in attachments)

    yield issue["id"], attachment_id, attachment_name

    api_client.delete_issue(Config.OAUTH_TOKEN, issue["id"])


@pytest.fixture
def create_two_issues_with_attachments(api_client):
    issues = []
    for i in range(2):
        issue_data = {
            "queue": {"key": Config.QUEUE_KEY},
            "summary": f"Test issue {i}",
            "type": "task"
        }
        issue = api_client.create_issue(Config.OAUTH_TOKEN, issue_data).json()

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(f"Content {i}".encode())
            tmp_path = tmp.name

        with open(tmp_path, "rb") as f:
            upload = api_client.upload_attachment(
                Config.OAUTH_TOKEN,
                issue["id"],
                {"file": f}
            ).json()

        os.unlink(tmp_path)
        issues.append((issue["id"], upload["id"], upload["name"]))

    yield issues
    for issue_id, _, _ in issues:
        api_client.delete_issue(Config.OAUTH_TOKEN, issue_id)


@pytest.fixture
def create_issue_with_image(api_client):
    img_buffer = io.BytesIO()
    img = Image.new("RGB", (100, 100), color="red")
    img.save(img_buffer, format="JPEG")
    img_buffer.seek(0)

    issue_data = {
        "queue": {"key": Config.QUEUE_KEY},
        "summary": "Image attachment issue",
        "type": "task"
    }
    issue = api_client.create_issue(Config.OAUTH_TOKEN, issue_data).json()

    files = {"file": ("test_image.jpg", img_buffer, "image/jpeg")}
    upload = api_client.upload_attachment(
        Config.OAUTH_TOKEN,
        issue["id"],
        files
    ).json()

    yield issue["id"], upload["id"], upload["name"]
    api_client.delete_issue(Config.OAUTH_TOKEN, issue["id"])


@pytest.fixture
def create_issue_with_large_attachment(api_client):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
        f.seek(15 * 1024 * 1024 - 1)
        f.write(b"\0")

    issue_data = {
        "queue": {"key": Config.QUEUE_KEY},
        "summary": "Large file issue",
        "type": "task"
    }
    issue = api_client.create_issue(Config.OAUTH_TOKEN, issue_data).json()

    with open(f.name, "rb") as file:
        upload = api_client.upload_attachment(
            Config.OAUTH_TOKEN,
            issue["id"],
            {"file": file}
        ).json()

    os.unlink(f.name)
    yield issue["id"], upload["id"], upload["name"]
    api_client.delete_issue(Config.OAUTH_TOKEN, issue["id"])


@pytest.fixture
def create_issue_with_image_attachment(api_client):
    img_buffer = io.BytesIO()
    img = Image.new("RGB", (100, 100), color="red")
    img.save(img_buffer, format="PNG")
    img_buffer.seek(0)

    issue_data = {
        "queue": {"key": Config.QUEUE_KEY},
        "summary": "Test image attachment issue",
        "type": "task"
    }
    issue_resp = api_client.create_issue(Config.OAUTH_TOKEN, issue_data)
    assert issue_resp.status_code in (200, 201)
    issue_id = issue_resp.json()["id"]

    files = {"file": ("test_image.png", img_buffer, "image/png")}
    upload_resp = api_client.upload_attachment(
        Config.OAUTH_TOKEN,
        issue_id,
        files
    )
    assert upload_resp.status_code in (200, 201)
    attachment = upload_resp.json()

    yield issue_id, attachment["id"]

    api_client.delete_issue(Config.OAUTH_TOKEN, issue_id)