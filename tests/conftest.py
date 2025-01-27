import asyncio

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.database.models import Base, User
from src.database.db import get_db
from src.services.users import UsersService
from src.services.tokens import TokensService
from src.schemas.users import UserCreateModel
from src.schemas.tokens import BaseTokenPayloadCreateModel
from src.utils.hashing import hash_secret
from src.main import app


engine = create_async_engine(
    "postgresql+asyncpg://postgres:12345@localhost:5432/postgres",
    poolclass=NullPool,
)

TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
)

test_user = UserCreateModel(
    email="user@gmail.com",
    password="12345678",
    username="test_user",
)


@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            hash_password = hash_secret(test_user.password)
            test_user.password = hash_password
            current_user = User(**test_user.model_dump())
            session.add(current_user)
            await session.commit()

    asyncio.run(init_models())


@pytest.fixture(scope="module")
def client():
    async def override_get_db():
        async with TestingSessionLocal() as session:
            try:
                yield session
            except Exception as err:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)


@pytest_asyncio.fixture(scope="module")
async def current_test_user():
    async with TestingSessionLocal() as session:
        users_service = UsersService(session)
        user = await users_service.get_by_email_or_none(email=test_user.email)
        if user is None:
            raise ValueError("Not found test user")
        return user


@pytest_asyncio.fixture()
async def get_access_token(current_test_user: User):
    async with TestingSessionLocal() as session:
        tokens_service = TokensService(session)
        token_payload = BaseTokenPayloadCreateModel(user_id=current_test_user.id)
        token = tokens_service.generate_access_token(token_payload)
        return token
