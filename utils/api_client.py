import requests
from config import Config

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

