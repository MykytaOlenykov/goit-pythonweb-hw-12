import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, UserStatus
from src.repository.users import UsersRepository
from src.schemas.users import UserCreateModel, UserStatus, UserStatusUpdateModel


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def users_repository(mock_session):
    return UsersRepository(mock_session)


@pytest.mark.asyncio
async def test_get_user_found(
    users_repository: UsersRepository, mock_session: AsyncMock
):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = User(
        id=1,
        username="username",
        email="email@gmail.com",
        avatar_url=None,
        status=UserStatus.VERIFIED,
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    filters = [User.id == 1]
    user = await users_repository.get_one_or_none(filters=filters)

    assert user is not None
    assert user.id == 1
    assert user.username == "username"


@pytest.mark.asyncio
async def test_get_user_not_found(
    users_repository: UsersRepository, mock_session: AsyncMock
):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    filters = [User.id == 2]
    user = await users_repository.get_one_or_none(filters=filters)

    assert user is None


@pytest.mark.asyncio
async def test_create_user(users_repository: UsersRepository, mock_session: AsyncMock):
    user = UserCreateModel(
        username="username",
        email="email@gmail.com",
        password="12345678",
    )

    result = await users_repository.create(body=user)

    assert isinstance(result, User)
    assert result.username == "username"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_update_user(users_repository: UsersRepository, mock_session: AsyncMock):
    user_data = UserStatusUpdateModel(status=UserStatus.VERIFIED)
    existing_user = User(
        id=1,
        username="username",
        email="email@gmail.com",
        avatar_url=None,
        status=UserStatus.REGISTERED,
    )
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_user
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await users_repository.update(user_id=1, body=user_data)

    assert result is not None
    assert result.status == UserStatus.VERIFIED
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(existing_user)


@pytest.mark.asyncio
async def test_not_update_user(
    users_repository: UsersRepository, mock_session: AsyncMock
):
    user_data = UserStatusUpdateModel(status=UserStatus.VERIFIED)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await users_repository.update(user_id=999, body=user_data)

    assert result is None
    mock_session.commit.assert_not_awaited()
    mock_session.refresh.assert_not_awaited()
