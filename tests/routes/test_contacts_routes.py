from datetime import date

import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import delete

from src.database.models import User, Contact
from src.utils.hashing import hash_secret

from tests.conftest import TestingSessionLocal


@pytest_asyncio.fixture(scope="module", autouse=True)
async def init_contacts_db_with_defaults(current_test_user: User):
    async with TestingSessionLocal() as session:
        another_user = User(
            email="another_user@gmail.com",
            password=hash_secret("12345678"),
            username="another_user",
        )

        session.add(another_user)
        await session.commit()
        await session.refresh(another_user)

        session.add_all(
            [
                Contact(
                    first_name="John",
                    last_name="Doe",
                    email="johndoe@example.com",
                    phone="1234567890",
                    user_id=current_test_user.id,
                    birthday=date(1990, 1, 1),
                ),
                Contact(
                    first_name="Jane",
                    last_name="Doe",
                    email="janedoe@example.com",
                    phone="0987654321",
                    user_id=current_test_user.id,
                    birthday=date(1995, 1, 1),
                ),
                Contact(
                    first_name="Alice",
                    last_name="Smith",
                    email="alicesmith@example.com",
                    phone="1122334455",
                    user_id=another_user.id,
                    birthday=date(1988, 7, 12),
                ),
            ]
        )
        await session.commit()


@pytest_asyncio.fixture(scope="module", autouse=True)
async def cleanup_contacts_db():
    yield

    async with TestingSessionLocal() as session:
        await session.execute(delete(Contact))
        await session.execute(
            delete(User).where(User.email == "another_user@gmail.com")
        )
        await session.commit()


def test_get_contacts(client: TestClient, get_access_token: str):
    response = client.get(
        "/api/contacts",
        headers={"Authorization": f"Bearer {get_access_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2

    # test search filter
    response = client.get(
        "/api/contacts",
        params={"search": "johndoe@example.com"},
        headers={"Authorization": f"Bearer {get_access_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1

    # test birthdays_within filter
    response = client.get(
        "/api/contacts",
        params={"birthdays_within": 7},
        headers={"Authorization": f"Bearer {get_access_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)


def test_get_contact_by_id(
    client: TestClient,
    get_access_token: str,
):
    response = client.get(
        "/api/contacts/1",
        headers={"Authorization": f"Bearer {get_access_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["id"] == 1
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["email"] == "johndoe@example.com"
    assert data["phone"] == "1234567890"
    assert data["birthday"] == "1990-01-01"

    # not found
    response = client.get(
        "/api/contacts/999",
        headers={"Authorization": f"Bearer {get_access_token}"},
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"


def test_create_contact(client: TestClient, get_access_token: str):
    response = client.post(
        "/api/contacts",
        json={
            "first_name": "Test_1",
            "last_name": "Test_2",
            "email": "test@example.com",
            "phone": "999888",
            "birthday": "2002-12-12",
        },
        headers={"Authorization": f"Bearer {get_access_token}"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert "id" in data
    assert data["first_name"] == "Test_1"
    assert data["last_name"] == "Test_2"
    assert data["email"] == "test@example.com"
    assert data["phone"] == "999888"
    assert data["birthday"] == "2002-12-12"

    # bad request/invalid body
    response = client.post(
        "/api/contacts",
        json={"first_name": "Test_1", "email": "test@example.com", "phone": "999888"},
        headers={"Authorization": f"Bearer {get_access_token}"},
    )
    assert response.status_code == 400, response.text
    data = response.json()
    assert isinstance(data["detail"], list)

    # bad request/invalid birthday
    response = client.post(
        "/api/contacts",
        json={
            "first_name": "Test_1",
            "last_name": "Test_2",
            "email": "test@example.com",
            "phone": "999888",
            "birthday": "12-12-2012",
        },
        headers={"Authorization": f"Bearer {get_access_token}"},
    )
    assert response.status_code == 400, response.text
    data = response.json()
    assert isinstance(data["detail"], str)
    assert data["detail"] == "Invalid date format. Expected YYYY-MM-DD"


def test_update_contact(client: TestClient, get_access_token: str):
    response = client.put(
        "/api/contacts/1",
        json={"phone": "111222"},
        headers={"Authorization": f"Bearer {get_access_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["phone"] == "111222"
    assert "id" in data

    # not found
    response = client.put(
        "/api/contacts/999",
        json={"phone": "111222"},
        headers={"Authorization": f"Bearer {get_access_token}"},
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"

    # bad request/invalid body
    response = client.put(
        "/api/contacts/1",
        json={"phone": 111222},
        headers={"Authorization": f"Bearer {get_access_token}"},
    )
    assert response.status_code == 400, response.text
    data = response.json()
    assert isinstance(data["detail"], list)

    # bad request/body has null
    response = client.put(
        "/api/contacts/1",
        json={"phone": None, "first_name": None},
        headers={"Authorization": f"Bearer {get_access_token}"},
    )
    assert response.status_code == 400, response.text
    data = response.json()
    assert isinstance(data["detail"], str)


def test_delete_contact(client: TestClient, get_access_token: str):
    response = client.delete(
        "/api/contacts/1",
        headers={"Authorization": f"Bearer {get_access_token}"},
    )
    assert response.status_code == 204
    assert response.content == b""

    # not found
    response = client.delete(
        "/api/contacts/1",
        headers={"Authorization": f"Bearer {get_access_token}"},
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == "Contact not found"
