from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from functools import cached_property

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from typing_extensions import override

from ...utils.orm import ORMUtils
from .base import BaseManager


class AsyncSessionManager(BaseManager):
    @override
    def get_engine(self) -> AsyncEngine:
        return ORMUtils.get_async_engine(self.config)

    @cached_property
    @override
    def engine(self) -> AsyncEngine:
        return ORMUtils.get_async_engine(self.config)

    @asynccontextmanager
    @override
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async_session = ORMUtils.get_async_session(self.engine)()

        try:
            yield async_session
        finally:
            await async_session.close()
