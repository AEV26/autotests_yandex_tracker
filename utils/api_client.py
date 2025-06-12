import requests
import os
from config import Config
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

class ChecklistItem(BaseModel):
    id: str
    text: str
    checked: bool
    assignee: Optional[Dict[str, Any]] = None

class TrackerApiClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"OAuth {token}",
            "X-Cloud-Org-ID": "bpfrvf6d7hoa6l9fforp"
        }
        self.session = requests.Session()

    def get_checklist_items(self, issue_id: str, params: dict = None) -> requests.Response:
        url = f"{self.base_url}/issues/{issue_id}/checklistItems"
        return requests.get(url, headers=self.headers, params=params)

    def post_checklist_item(self, issue_id: str, data: dict) -> requests.Response:
        url = f"{self.base_url}/issues/{issue_id}/checklistItems"
        return requests.post(url, headers=self.headers, json=data)

    def patch_checklist_item(self, issue_id: str, item_id: str, data: dict) -> requests.Response:
        url = f"{self.base_url}/issues/{issue_id}/checklistItems/{item_id}"
        return requests.patch(url, headers=self.headers, json=data)

    def delete_checklist_items(self, issue_id: str) -> requests.Response:
        url = f"{self.base_url}/issues/{issue_id}/checklistItems"
        return requests.delete(url, headers=self.headers)

    def delete_single_checklist_item(self, issue_id: str, item_id: str, params: dict = None) -> requests.Response:
        url = f"{self.base_url}/issues/{issue_id}/checklistItems/{item_id}"
        return requests.delete(url, headers=self.headers, params=params)

    def link_issues(self, issue_id: str, payload: dict) -> requests.Response:
        url = f"{self.base_url}/issues/{issue_id}/links"
        return requests.post(url, headers=self.headers, json=payload)

    def get_issue_links(self, issue_id: str, params: dict = None) -> requests.Response:
        url = f"{self.base_url}/issues/{issue_id}/links"
        return requests.get(url, headers=self.headers, params=params)

    def delete_issue_link(self, issue_id: str, link_id: str) -> requests.Response:
        url = f"{self.base_url}/issues/{issue_id}/links/{link_id}"
        return requests.delete(url, headers=self.headers)

    def find_link_id(self, issue_id: str, related_issue_key: str) -> Optional[str]:
        response = self.get_issue_links(issue_id)
        if response.status_code == 200:
            for link in response.json():
                if link.get("object", {}).get("key") == related_issue_key:
                    return str(link.get("id"))
        return None

    def get_global_fields(self, params: dict = None) -> requests.Response:
        url = f"{self.base_url}/fields"
        return requests.get(url, headers=self.headers, params=params)

    def create_issue_field(self, payload: dict) -> requests.Response:
        url = f"{self.base_url}/fields"
        return requests.post(url, headers=self.headers, json=payload)

    def get_field_by_id(self, field_id: str):
        return requests.get(
            f"{self.base_url}/fields/{field_id}",
            headers=self.headers
        )

    def patch_field_name(self, field_id: str, data: dict, version: int | None = None) -> requests.Response:
        url = f"{self.base_url}/fields/{field_id}"
        if version is not None:
            url += f"?version={version}"
        return requests.patch(url, headers=self.headers, json=data)

    def patch_field_options(self, field_id: str, data: dict, version: int) -> requests.Response:
        url = f"{self.base_url}/fields/{field_id}?version={version}"
        return requests.patch(url, headers=self.headers, json=data)

    def create_field_category(self, data: dict) -> requests.Response:
        url = f"{self.base_url}/fields/categories"
        return requests.post(url, headers=self.headers, json=data)

    def get_field_categories(self, params: dict = None) -> requests.Response:
        url = f"{self.base_url}/fields/categories"
        return requests.get(url, headers=self.headers, params=params)

    def post_project_checklist_item(self, entity_type, entity_id, data):
        url = f"{self.base_url}/entities/{entity_type}/{entity_id}/checklistItems"
        return requests.post(url, headers=self.headers, json=data)

    def post_multiple_project_checklist_items(self, entity_type: str, entity_id: str, data: list):
        url = f"{self.base_url}/entities/{entity_type}/{entity_id}/checklistItems?fields=checklistItems"
        return self.session.post(url, headers=self.headers, json=data)

class TrackerAPIClient:
    def __init__(self):
        self.base_url = Config.TRACKER_API_URL
        self.default_headers = {
            "Content-Type": "application/json",
            "X-Cloud-Org-ID": Config.ORG_ID
        }

    def add_comment(self, token, issue_id, comment_data):
        headers = {
            "Authorization": f"OAuth {token}",
            "X-Cloud-Org-ID": Config.ORG_ID,
            "Content-Type": "application/json"
        }
        return requests.post(
            f"{self.base_url}/issues/{issue_id}/comments",
            headers=headers,
            json=comment_data
        )

    def get_comments(self, token, issue_id):
        headers = {
            "Authorization": f"OAuth {token}",
            "X-Cloud-Org-ID": Config.ORG_ID,
            "Content-Type": "application/json"
        }
        return requests.get(
            f"{self.base_url}/issues/{issue_id}/comments",
            headers=headers
        )

    def delete_issue(self, token, issue_id):
        headers = {
            "Authorization": f"OAuth {token}",
            "X-Cloud-Org-ID": Config.ORG_ID
        }
        return requests.delete(
            f"{self.base_url}/issues/{issue_id}",
            headers=headers
        )

    def delete_comment(self, token, issue_id, comment_id):
        headers = {
            "Authorization": f"OAuth {token}",
            "X-Cloud-Org-ID": Config.ORG_ID
        }
        return requests.delete(
            f"{self.base_url}/issues/{issue_id}/comments/{comment_id}",
            headers=headers
        )

    def create_issue(self, token, issue_data):
        headers = {
            "Authorization": f"OAuth {token}",
            "X-Cloud-Org-ID": Config.ORG_ID,
            "Content-Type": "application/json"
        }
        return requests.post(
            f"{self.base_url}/issues",
            headers=headers,
            json=issue_data
        )

    def update_comment(self, token, issue_id, comment_id, comment_data):
        headers = {
            "Authorization": f"OAuth {token}",
            "X-Cloud-Org-ID": Config.ORG_ID,
            "Content-Type": "application/json"
        }
        return requests.patch(
            f"{self.base_url}/issues/{issue_id}/comments/{comment_id}",
            headers=headers,
            json=comment_data
        )

    def get_attachments(self, token, issue_id, params=None):
        headers = {
            "Authorization": f"OAuth {token}",
            "X-Cloud-Org-ID": Config.ORG_ID,
            "Content-Type": "application/json"
        }
        return requests.get(
            f"{self.base_url}/issues/{issue_id}/attachments",
            headers=headers,
            params=params or {}
        )

    def upload_attachment(self, token, issue_id, files):
        headers = {
            "Authorization": f"OAuth {token}",
            "X-Cloud-Org-ID": Config.ORG_ID
        }
        return requests.post(
            f"{Config.TRACKER_API_URL}/issues/{issue_id}/attachments/",
            headers=headers,
            files=files
        )

    def delete_attachment(self, token, issue_id, attachment_id):
        headers = {
            "Authorization": f"OAuth {token}",
            "X-Cloud-Org-ID": Config.ORG_ID
        }
        url = f"{Config.TRACKER_API_URL}/issues/{issue_id}/attachments/{attachment_id}"
        return requests.delete(url, headers=headers)

    def download_attachment(self, token, issue_id, attachment_id, file_name):
        headers = {
            "Authorization": f"OAuth {token}",
            "X-Cloud-Org-ID": Config.ORG_ID
        }
        return requests.get(
            f"{self.base_url}/issues/{issue_id}/attachments/{attachment_id}/{file_name}",
            headers=headers,
            stream=True
        )

    def download_thumbnail(self, token, issue_id, attachment_id):
        headers = {
            "Authorization": f"OAuth {token}",
            "X-Cloud-Org-ID": Config.ORG_ID
        }
        url = f"{self.base_url}/issues/{issue_id}/thumbnails/{attachment_id}"
        return requests.get(url, headers=headers, stream=True)

    def upload_temp_attachment(self, token, files):
        headers = {
            "Authorization": f"OAuth {token}",
            "X-Cloud-Org-ID": Config.ORG_ID
        }
        url = f"{self.base_url}/attachments/"
        return requests.post(url, headers=headers, files=files)

    def get_myself(self, token):
        headers = {
            "Authorization": f"OAuth {token}",
            "X-Cloud-Org-ID": Config.ORG_ID
        }
        url = f"{self.base_url}/myself"
        return requests.get(url, headers=headers)

    def get_users(self, token, params=None):
        headers = {
            "Authorization": f"OAuth {token}",
            "X-Cloud-Org-ID": Config.ORG_ID
        }
        url = f"{self.base_url}/users"
        return requests.get(url, headers=headers, params=params or {})

    def get_user(self, token, user_id_or_login):
        headers = {
            "Authorization": f"OAuth {token}",
            "X-Cloud-Org-ID": Config.ORG_ID
        }
        url = f"{self.base_url}/users/{user_id_or_login}"
        return requests.get(url, headers=headers)

    def add_entity_comment(self, token, entity_type, entity_id, comment_data):
        headers = {
            "Authorization": f"OAuth {token}",
            "X-Cloud-Org-ID": Config.ORG_ID,
            "Content-Type": "application/json"
        }
        return requests.post(
            f"{self.base_url}/entities/{entity_type}/{entity_id}/comments",
            headers=headers,
            json=comment_data
        )

    def get_entity_comments(self, token, entity_type, entity_id):
        headers = {
            "Authorization": f"OAuth {token}",
            "X-Cloud-Org-ID": Config.ORG_ID,
            "Content-Type": "application/json"
        }
        return requests.get(
            f"{self.base_url}/entities/{entity_type}/{entity_id}/comments",
            headers=headers
        )

    def get_entity_comment(self, token, entity_type, entity_id, comment_id):
        headers = {
            "Authorization": f"OAuth {token}",
            "X-Cloud-Org-ID": Config.ORG_ID,
            "Content-Type": "application/json"
        }
        return requests.get(
            f"{self.base_url}/entities/{entity_type}/{entity_id}/comments/{comment_id}",
            headers=headers
        )

    def update_entity_comment(self, token, entity_type, entity_id, comment_id, comment_data):
        headers = {
            "Authorization": f"OAuth {token}",
            "X-Cloud-Org-ID": Config.ORG_ID,
            "Content-Type": "application/json"
        }
        return requests.patch(
            f"{self.base_url}/entities/{entity_type}/{entity_id}/comments/{comment_id}",
            headers=headers,
            json=comment_data
        )

    def delete_entity_comment(self, token, entity_type, entity_id, comment_id, params=None):
        headers = {
            "Authorization": f"OAuth {token}",
            "X-Cloud-Org-ID": Config.ORG_ID
        }
        return requests.delete(
            f"{self.base_url}/entities/{entity_type}/{entity_id}/comments/{comment_id}",
            headers=headers,
            params=params or {}
        )

class Tracker_API_Client:
    def __init__(self):
        self.base_url = Config.TRACKER_API_URL
        self.headers = {
            "Authorization": f"OAuth {os.getenv('TRACKER_TOKEN')}",
            "X-Cloud-Org-ID": os.getenv("TRACKER_CLOUD_ORG_ID"),
            "Content-Type": "application/json"
        }

    def create_issue(self, issue_data: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> requests.Response:
        url = f"{self.base_url}/issues/"
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)
        return requests.post(url, json=issue_data, headers=request_headers)

    def patch_issue(self, issue_id: str, update_data: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> requests.Response:
        url = f"{self.base_url}/issues/{issue_id}"
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)

        return requests.patch(url, json=update_data, headers=request_headers)\

    def get_issue(self, issue_id: str, headers: Optional[Dict[str, str]] = None) -> requests.Response:
        url = f"{self.base_url}/issues/{issue_id}"
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)
        return requests.get(url, headers=request_headers)

    def get_issue_count(self, filter_params: Dict[str, Any] = None, headers: Optional[Dict[str, str]] = None) -> requests.Response:
        url = f"{self.base_url}/issues/_count"
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)
        return requests.post(url, json=filter_params, headers=request_headers)

    def search_issues(self, search_params: Dict[str, Any] = None, headers: Optional[Dict[str, str]] = None) -> requests.Response:
        url = f"{self.base_url}/issues/_search?expand=transitions"
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)
        return requests.post(url, json=search_params, headers=request_headers)

    def move_issue(self, issue_id: str, queue: str, move_data: Dict[str, Any] = None, headers: Optional[Dict[str, str]] = None) -> requests.Response:
        url = f"{self.base_url}/issues/{issue_id}/_move?queue={queue}"
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)
        return requests.post(url, json=move_data or {}, headers=request_headers)

    def get_issue_changelog(self, issue_id: str, headers: Optional[Dict[str, str]] = None) -> requests.Response:
        url = f"{self.base_url}/issues/{issue_id}/changelog"
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)
        return requests.get(url, headers=request_headers)

    def get_issue_transitions(self, issue_id: str, headers: Optional[Dict[str, str]] = None) -> requests.Response:
        url = f"{self.base_url}/issues/{issue_id}/transitions"
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)
        return requests.get(url, headers=request_headers)

    def execute_issue_transition(self, issue_id: str, transition_id: str, transition_data: Dict[str, Any] = None,
                                 headers: Optional[Dict[str, str]] = None) -> requests.Response:
        url = f"{self.base_url}/issues/{issue_id}/transitions/{transition_id}"
        request_headers = self.headers.copy()
        if headers:
            request_headers.update(headers)
        return requests.post(url, json=transition_data or {}, headers=request_headers)