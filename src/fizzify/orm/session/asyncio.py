import logging
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
        logging.info(f"Getting engine for {self.config.database}")

        return ORMUtils.get_async_engine(self.config, self.engine_config)

    @cached_property
    @override
    def engine(self) -> AsyncEngine:
        logging.info(f"Getting engine for {self.config.database}")

        return ORMUtils.get_async_engine(self.config, self.engine_config)

    @asynccontextmanager
    @override
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        logging.info(f"Getting session for {self.config.database}")

        async_session = await self.create_session()

        try:
            yield async_session
        finally:
            logging.info(f"Closing session for {self.config.database}")

            await self.close_session(async_session)

    @override
    async def create_session(self) -> AsyncSession:
        """
        Create a new session.
        """
        return ORMUtils.get_async_session(self.engine)()

    @override
    async def close_session(self, async_session: AsyncSession):
        """
        Close the session.
        """
        await async_session.close()
