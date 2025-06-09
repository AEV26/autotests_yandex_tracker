import requests
from typing import Optional, Dict, Any
from pydantic import BaseModel


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
        """
        DELETE https://api.tracker.yandex.net/v3/issues/<id_задачи>/checklistItems/<id_пункта_чеклиста>
        """
        url = f"{self.base_url}/issues/{issue_id}/checklistItems/{item_id}"
        return requests.delete(url, headers=self.headers, params=params)

    def link_issues(self, issue_id: str, payload: dict) -> requests.Response:
        """
        POST https://api.tracker.yandex.net/v3/issues/<issue_id>/links
        Связывание задач
        """
        url = f"{self.base_url}/issues/{issue_id}/links"
        return requests.post(url, headers=self.headers, json=payload)

    def get_issue_links(self, issue_id: str, params: dict = None) -> requests.Response:
        """
        Получить связи задачи
        GET https://api.tracker.yandex.net/v3/issues/<issue_id>/links
        """
        url = f"{self.base_url}/issues/{issue_id}/links"
        return requests.get(url, headers=self.headers, params=params)
    def delete_issue_link(self, issue_id: str, link_id: str) -> requests.Response:
        """
        DELETE https://api.tracker.yandex.net/v3/issues/<issue_id>/links/<link_id>
        Удаление связи задачи
        """
        url = f"{self.base_url}/issues/{issue_id}/links/{link_id}"
        return requests.delete(url, headers=self.headers)

    def find_link_id(self, issue_id: str, related_issue_key: str) -> Optional[str]:
        """
        Ищет ID связи задачи по ключу связанной задачи
        """
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




