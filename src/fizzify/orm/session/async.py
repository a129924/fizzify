from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from typing_extensions import override

from ...utils.orm import ORMUtils
from .base import BaseManager


class AsyncSessionManager(BaseManager):
    @override
    def get_engine(self) -> AsyncEngine:
        return ORMUtils.get_async_engine(self.config)

    @asynccontextmanager
    @override
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async_session = ORMUtils.get_async_session(self.get_engine())()
        yield async_session
        await async_session.close()
