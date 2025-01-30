import time
from unittest.mock import Mock

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import select, delete

from src.database.models import User, UserStatus, Token, TokenType
from src.services.users import UsersService
from src.services.tokens import TokensService
from src.schemas.tokens import BaseTokenPayloadCreateModel
from src.utils.hashing import hash_secret

from tests.conftest import TestingSessionLocal, test_user

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
    "username": "verified",
    "email": "verified@gmail.com",
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


@pytest_asyncio.fixture
async def get_verification_token():
    async with TestingSessionLocal() as session:
        await session.execute(delete(Token))
        await session.commit()
        user = await UsersService(session).get_by_email_or_none(
            new_user_data.get("email")
        )
        if user is None:
            raise ValueError("Not found test user")
        payload = BaseTokenPayloadCreateModel(user_id=user.id)
        token = await TokensService(session).create_token(
            token_type=TokenType.VERIFICATION,
            payload=payload,
        )
        return token.token


@pytest_asyncio.fixture
async def get_reset_token():
    async with TestingSessionLocal() as session:
        await session.execute(delete(Token))
        await session.commit()
        user = await UsersService(session).get_by_email_or_none(
            verified_user_data.get("email")
        )
        if user is None:
            raise ValueError("Not found test user")
        payload = BaseTokenPayloadCreateModel(user_id=user.id)
        token = await TokensService(session).create_token(
            token_type=TokenType.RESET,
            payload=payload,
        )
        return token.token


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

    # invalid email
    response = client.post(
        "api/auth/signup",
        json={
            "username": "test",
            "email": "invalid-email",
            "password": "12345678",
        },
    )
    assert response.status_code == 400, response.text


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


def test_logout(client: TestClient, get_access_token: str):
    # login for get refresh_token
    login_response = client.post(
        "api/auth/login",
        json={
            "email": test_user.email,
            "password": test_user.password,
        },
    )
    assert login_response.status_code == 200, login_response.text
    refresh_token = login_response.cookies.get("refresh_token")

    # logout
    client.cookies.set("refresh_token", refresh_token)
    response = client.post(
        "api/auth/logout",
        headers={"Authorization": f"Bearer {get_access_token}"},
    )
    assert response.status_code == 204, response.text
    assert response.cookies.get("refresh_token") is None

    # Invalid refresh token
    client.cookies.set("refresh_token", refresh_token)
    response = client.post(
        "api/auth/logout",
        headers={"Authorization": f"Bearer {get_access_token}"},
    )
    assert response.status_code == 401, response.text
    assert response.json()["detail"] == "Invalid refresh token"


def test_refresh(client: TestClient):
    # login for get refresh_token
    login_response = client.post(
        "api/auth/login",
        json={
            "email": test_user.email,
            "password": test_user.password,
        },
    )
    assert login_response.status_code == 200, login_response.text
    refresh_token = login_response.cookies.get("refresh_token")
    time.sleep(1)

    # refresh
    client.cookies.set("refresh_token", refresh_token)
    response = client.post(
        "api/auth/refresh",
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert response.cookies.get("refresh_token") is not None

    # Invalid refresh
    client.cookies.set("refresh_token", "refresh_token")
    response = client.post(
        "api/auth/refresh",
    )
    assert response.status_code == 401, response.text


def test_resend_verification_email(client: TestClient, monkeypatch):
    # user not found
    response = client.post("api/auth/verify", json={"email": "not_found@gmail.com"})
    assert response.status_code == 401, response.text
    assert response.json()["detail"] == "Invalid email"

    # already verified
    response = client.post(
        "api/auth/verify",
        json={"email": verified_user_data.get("email")},
    )
    assert response.status_code == 409, response.text
    assert response.json()["detail"] == "User is already verified"

    # resend verification email
    mock_send_email = Mock()
    monkeypatch.setattr("src.services.mail.MailService.send_mail", mock_send_email)
    response = client.post(
        "api/auth/verify",
        json={"email": new_user_data.get("email")},
    )
    assert response.status_code == 200, response.text
    assert response.json()["message"] == (
        "Please check your email to activate your account."
    )


def test_verify_user(client: TestClient, get_verification_token: str):
    # invalid token
    response = client.get("api/auth/verify/invalid-token")
    assert response.status_code == 401, response.text
    assert response.json()["detail"] == "Invalid token"

    # verify user
    response = client.get(
        f"api/auth/verify/{get_verification_token}",
    )
    assert response.status_code == 200, response.text
    assert response.json()["message"] == (
        "Your email has been successfully verified. You can now log in to your account."
    )


def test_me(client: TestClient, get_access_token: str):
    response = client.get(
        "api/auth/me",
        headers={"Authorization": f"Bearer {get_access_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert "id" in data
    assert "username" in data
    assert "email" in data
    assert "avatar_url" in data


def test_forgot_password(client: TestClient, monkeypatch):
    # user not found
    response = client.post(
        "api/auth/reset-password",
        json={"email": "not_found@gmail.com"},
    )
    assert response.status_code == 200, response.text
    assert response.json()["message"] == (
        "If this email exists, we have sent password reset instructions."
    )

    # forgot password
    mock_send_email = Mock()
    monkeypatch.setattr("src.services.mail.MailService.send_mail", mock_send_email)
    response = client.post(
        "api/auth/reset-password",
        json={"email": new_user_data.get("email")},
    )
    assert response.status_code == 200, response.text
    assert response.json()["message"] == (
        "If this email exists, we have sent password reset instructions."
    )


def test_reset_password(client: TestClient, get_reset_token: str):
    # invalid token
    response = client.post(
        "api/auth/reset-password/invalid-token",
        json={"password": "88888888"},
    )
    assert response.status_code == 401, response.text
    assert response.json()["detail"] == "Invalid token"

    # invalid body
    response = client.post(
        f"api/auth/reset-password/{get_reset_token}",
        json={"password": "123"},
    )
    assert response.status_code == 400, response.text
    data = response.json()
    assert "detail" in data
    assert isinstance(data["detail"], list)

    # change password
    response = client.post(
        f"api/auth/reset-password/{get_reset_token}",
        json={"password": "88888888"},
    )
    assert response.status_code == 200, response.text
    assert response.json()["message"] == (
        "Your password has been successfully changed."
    )
