import contextlib
from typing import Any, AsyncGenerator

from redis.asyncio import Redis

from src.settings import settings


class RedisSessionManager:
    def __init__(self, url: str, connection_kwargs: dict[str, Any] | None = None):
        self._url = url
        self._connection_kwargs = connection_kwargs or {}
        self._redis: Redis | None = None

    async def initialize(self):
        if self._redis is None:
            self._redis = Redis.from_url(self._url, **self._connection_kwargs)

    async def close(self):
        if self._redis:
            await self._redis.close()
            self._redis = None

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncGenerator[Redis, None]:
        if self._redis is None:
            await self.initialize()
        try:
            yield self._redis
        finally:
            await self.close()


redis_manager = RedisSessionManager(settings.REDIS_URL)


async def get_redis() -> AsyncGenerator[Redis, None]:
    async with redis_manager.session() as redis_conn:
        yield redis_conn
