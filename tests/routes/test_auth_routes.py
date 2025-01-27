from unittest.mock import Mock

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import select, delete

from src.database.models import User, UserStatus, Token, TokenType
from src.services.tokens import TokensService
from src.schemas.tokens import BaseTokenPayloadCreateModel
from src.utils.hashing import hash_secret

from tests.conftest import TestingSessionLocal

new_user_data = {
    "username": "test",
    "email": "test@gmail.com",
    "password": "12345678",
}

deleted_user_data = {
    "username": "deleted",
    "email": "deleted@gmail.com",
    "password": "12345678",
}

verified_user_data = {
    "username": "verified_1",
    "email": "verified_1@gmail.com",
    "password": "12345678",
}


@pytest_asyncio.fixture(scope="module", autouse=True)
async def init_contacts_db_with_defaults():
    async with TestingSessionLocal() as session:
        session.add_all(
            [
                User(
                    username=deleted_user_data.get("username"),
                    email=deleted_user_data.get("email"),
                    password=hash_secret(deleted_user_data.get("password")),
                    status=UserStatus.DELETED,
                ),
                User(
                    username=verified_user_data.get("username"),
                    email=verified_user_data.get("email"),
                    password=hash_secret(verified_user_data.get("password")),
                    status=UserStatus.VERIFIED,
                ),
            ]
        )
        await session.commit()


def test_signup(client: TestClient, monkeypatch):
    mock_send_email = Mock()
    monkeypatch.setattr("src.services.mail.MailService.send_mail", mock_send_email)
    response = client.post("api/auth/signup", json=new_user_data)

    assert response.status_code == 200, response.text
    assert response.json()["message"] == (
        "Registration successful. Please check your email to activate your account."
    )

    # conflict
    response = client.post("api/auth/signup", json=new_user_data)
    assert response.status_code == 409, response.text
    assert response.json()["detail"] == "This email is already signed up"


def test_login(client: TestClient):
    # not found
    response = client.post(
        "api/auth/login",
        json={
            "email": "test_not_found@gmail.com",
            "password": "qweqwe123123",
        },
    )
    assert response.status_code == 401, response.text
    assert response.json()["detail"] == "Invalid email or password"

    # not confirmed
    response = client.post(
        "api/auth/login",
        json={
            "email": new_user_data.get("email"),
            "password": new_user_data.get("password"),
        },
    )
    assert response.status_code == 401, response.text
    assert response.json()["detail"] == "User needs to verify their account"

    # user account is deleted
    response = client.post(
        "api/auth/login",
        json={
            "email": deleted_user_data.get("email"),
            "password": deleted_user_data.get("password"),
        },
    )
    assert response.status_code == 401, response.text
    assert response.json()["detail"] == "User account is deleted"

    # invalid password
    response = client.post(
        "api/auth/login",
        json={
            "email": verified_user_data.get("email"),
            "password": "qweqweqwe",
        },
    )
    assert response.status_code == 401, response.text
    assert response.json()["detail"] == "Invalid email or password"

    # login
    response = client.post(
        "api/auth/login",
        json={
            "email": verified_user_data.get("email"),
            "password": verified_user_data.get("password"),
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert response.cookies.get("refresh_token") is not None
