import contextlib
from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from src.settings import settings


class DatabaseSessionManager:

    def __init__(self, url: str, engine_kwargs: dict[str, Any] | None = None):
        self._engine: AsyncEngine | None = create_async_engine(
            url, **(engine_kwargs or {})
        )
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        if self._session_maker is None:
            raise Exception("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(settings.DB_URL, {"echo": settings.ECHO_SQL})


async def get_db():
    async with sessionmanager.session() as session:
        yield session
