import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, UserStatus, Contact
from src.repository.contacts import ContactsRepository
from src.schemas.contacts import ContactCreateModel, ContactUpdateModel


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def contacts_repository(mock_session):
    return ContactsRepository(mock_session)


@pytest.fixture
def user():
    return User(
        id=1,
        username="username",
        email="email@gmail.com",
        avatar_url=None,
        status=UserStatus.VERIFIED,
    )


@pytest.fixture
def existing_contact(user: User):
    return Contact(
        id=1,
        first_name="Mango",
        last_name="Tomato",
        email="tomato@gmail.com",
        phone="012839123",
        birthday="2012-12-12",
        user_id=user.id,
    )


@pytest.mark.asyncio
async def test_get_contacts(
    contacts_repository: ContactsRepository,
    mock_session: AsyncMock,
    existing_contact: Contact,
):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [existing_contact]
    mock_session.execute = AsyncMock(return_value=mock_result)

    contacts = await contacts_repository.get_all(offset=0, limit=10)

    assert len(contacts) == 1
    assert contacts[0].first_name == "Mango"


@pytest.mark.asyncio
async def test_get_contact(
    contacts_repository: ContactsRepository,
    mock_session: AsyncMock,
    existing_contact: Contact,
):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    filters = [Contact.id == existing_contact.id]
    contact = await contacts_repository.get_one_or_none(filters=filters)

    assert contact is not None
    assert contact.id == existing_contact.id
    assert contact.first_name == "Mango"


@pytest.mark.asyncio
async def test_create_contact(
    contacts_repository: ContactsRepository,
    mock_session: AsyncMock,
    user: User,
):
    contact = ContactCreateModel(
        first_name="Mango",
        last_name="Tomato",
        email="tomato@gmail.com",
        phone="012839123",
        birthday="2012-12-12",
    )

    result = await contacts_repository.create(user_id=user.id, body=contact)

    assert isinstance(result, Contact)
    assert result.first_name == "Mango"
    assert result.user_id == user.id
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_update_contact(
    contacts_repository: ContactsRepository,
    mock_session: AsyncMock,
    existing_contact: Contact,
):
    contact_data = ContactUpdateModel(
        first_name="Test_1",
        last_name="Test_2",
        email="email@gmail.com",
        phone="009999999",
        birthday="2012-12-12",
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contacts_repository.update(
        contact_id=existing_contact.id,
        body=contact_data,
    )

    assert result is not None
    assert result.first_name == "Test_1"
    assert result.last_name == "Test_2"
    assert result.email == "email@gmail.com"
    assert result.phone == "009999999"
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(existing_contact)


@pytest.mark.asyncio
async def test_not_update_user(
    contacts_repository: ContactsRepository,
    mock_session: AsyncMock,
):
    contact_data = ContactUpdateModel(
        first_name="Mango",
        last_name="Tomato",
        email="tomato@gmail.com",
        phone="012839123",
        birthday="2012-12-12",
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contacts_repository.update(contact_id=999, body=contact_data)

    assert result is None
    mock_session.commit.assert_not_awaited()
    mock_session.refresh.assert_not_awaited()


@pytest.mark.asyncio
async def test_delete_contact(
    contacts_repository: ContactsRepository,
    mock_session: AsyncMock,
    existing_contact: Contact,
):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_contact
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await contacts_repository.delete(contact=existing_contact)

    assert result is not None
    assert result.id == existing_contact.id
    mock_session.delete.assert_awaited_once_with(existing_contact)
    mock_session.commit.assert_awaited_once()
