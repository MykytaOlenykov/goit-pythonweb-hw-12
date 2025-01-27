from unittest.mock import patch

from fastapi.testclient import TestClient


@patch("src.services.upload_file.UploadFileService.upload_file")
def test_change_avatar(
    mock_upload_file,
    client: TestClient,
    get_access_token: str,
):
    fake_url = "<http://example.com/avatar.jpg>"
    mock_upload_file.return_value = fake_url

    file_data = {"avatar": ("avatar.jpg", b"fake image content", "image/jpeg")}

    response = client.put(
        "/api/users/avatars",
        headers={"Authorization": f"Bearer {get_access_token}"},
        files=file_data,
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["avatar_url"] == fake_url
    mock_upload_file.assert_called_once()
