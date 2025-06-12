import pytest
import allure
from config import Config


@allure.feature("API Яндекс.Трекера")
@allure.story("Работа с миниатюрами вложений")
class TestThumbnailsAPI:

    @allure.title("Скачивание миниатюры с невалидным токеном")
    def test_download_thumbnail_unauthorized(self, api_client, create_issue_with_image_attachment):
        issue_id, attachment_id = create_issue_with_image_attachment

        response = api_client.download_thumbnail(
            Config.INVALID_TOKEN,
            issue_id,
            attachment_id
        )

        assert response.status_code == 401
        assert "application/json" in response.headers["Content-Type"]

    @allure.title("Скачивание миниатюры несуществующего вложения")
    def test_download_nonexistent_thumbnail(self, api_client, create_test_issue):
        issue_id = create_test_issue

        response = api_client.download_thumbnail(
            Config.OAUTH_TOKEN,
            issue_id,
            "999999999"
        )

        assert response.status_code == 404

    @allure.title("Попытка получить миниатюру для текстового файла")
    def test_thumbnail_for_non_image(self, api_client, create_issue_with_attachment):
        issue_id, attachment_id, _ = create_issue_with_attachment

        response = api_client.download_thumbnail(
            Config.OAUTH_TOKEN,
            issue_id,
            attachment_id
        )

        assert response.status_code in [400, 404]

    @allure.title("Скачивание миниатюры после удаления вложения")
    def test_download_thumbnail_after_delete(self, api_client, create_issue_with_image_attachment):
        issue_id, attachment_id = create_issue_with_image_attachment

        del_resp = api_client.delete_attachment(
            Config.OAUTH_TOKEN,
            issue_id,
            attachment_id
        )
        assert del_resp.status_code == 204

        response = api_client.download_thumbnail(
            Config.OAUTH_TOKEN,
            issue_id,
            attachment_id
        )
        assert response.status_code in [404, 410]

    @allure.title("Скачивание миниатюры для вложения из другой задачи")
    def test_download_thumbnail_cross_issue(self, api_client, create_issue_with_image_attachment, create_test_issue):
        _, attachment_id = create_issue_with_image_attachment
        other_issue_id = create_test_issue

        response = api_client.download_thumbnail(
            Config.OAUTH_TOKEN,
            other_issue_id,
            attachment_id
        )
        assert response.status_code in [403, 404]

    @allure.title("Скачивание миниатюры с некорректным issue_id")
    def test_download_thumbnail_invalid_issue(self, api_client, create_issue_with_image_attachment):
        _, attachment_id = create_issue_with_image_attachment

        response = api_client.download_thumbnail(
            Config.OAUTH_TOKEN,
            "INVALID-ISSUE-ID",
            attachment_id
        )
        assert response.status_code in [400, 404]
