import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, UserStatus, Token, TokenType
from src.repository.tokens import TokensRepository
from src.schemas.tokens import TokenCreateModel


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def tokens_repository(mock_session):
    return TokensRepository(mock_session)


@pytest.fixture
def user():
    return User(
        id=1,
        username="username",
        email="email@gmail.com",
        avatar_url=None,
        status=UserStatus.VERIFIED,
    )


@pytest.mark.asyncio
async def test_get_tokens(tokens_repository: TokensRepository, mock_session: AsyncMock):
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        Token(id=1, token="token1", type=TokenType.REFRESH, user_id=1),
    ]
    mock_session.execute = AsyncMock(return_value=mock_result)

    tokens = await tokens_repository.get_all(offset=0, limit=10)

    assert len(tokens) == 1
    assert tokens[0].type == TokenType.REFRESH


@pytest.mark.asyncio
async def test_get_token_found(
    tokens_repository: TokensRepository,
    mock_session: AsyncMock,
    user: User,
):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = Token(
        id=1, token="token1", type=TokenType.REFRESH, user_id=1
    )
    mock_session.execute = AsyncMock(return_value=mock_result)

    filters = [Token.id == 1, Token.user == user]
    token = await tokens_repository.get_one_or_none(filters=filters)

    assert token is not None
    assert token.id == 1
    assert token.type == TokenType.REFRESH


@pytest.mark.asyncio
async def test_create_token(
    tokens_repository: TokensRepository,
    mock_session: AsyncMock,
    user: User,
):
    token = TokenCreateModel(type=TokenType.REFRESH, token="token1", user_id=user.id)

    result = await tokens_repository.create(body=token)

    assert isinstance(result, Token)
    assert result.token == "token1"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(result)


@pytest.mark.asyncio
async def test_delete_token(
    tokens_repository: TokensRepository,
    mock_session: AsyncMock,
):
    existing_token = Token(id=1, token="token1", type=TokenType.REFRESH, user_id=1)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_token
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await tokens_repository.delete(token=existing_token)

    assert result is not None
    assert result.id == 1
    mock_session.delete.assert_awaited_once_with(existing_token)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_many_tokens(
    tokens_repository: TokensRepository,
    mock_session: AsyncMock,
):
    existing_tokens = ["token1", "token2"]
    mock_result = MagicMock()
    mock_result.rowcount = 2
    mock_session.execute = AsyncMock(return_value=mock_result)

    result = await tokens_repository.delete_many(tokens=existing_tokens)

    assert result == 2
    mock_session.execute.assert_called_once()
    mock_session.commit.assert_awaited_once()
