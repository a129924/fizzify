import logging
from collections.abc import Generator
from contextlib import contextmanager
from functools import cached_property

from sqlalchemy import Engine
from sqlalchemy.orm import Session
from typing_extensions import override

from ...utils.orm import ORMUtils
from .base import BaseManager


class SyncSessionManager(BaseManager):
    """
    Manager for synchronous sessions.
    """

    @override
    def get_engine(self) -> Engine:
        """
        Get the engine for the synchronous session.
        """
        logging.info(f"Getting engine for {self.config.database}")

        return ORMUtils.get_engine(self.config, self.engine_config)

    @cached_property
    @override
    def engine(self) -> Engine:
        return ORMUtils.get_engine(self.config, self.engine_config)

    @contextmanager
    @override
    def get_session(self) -> Generator[Session, None, None]:
        """
        Get the session for the synchronous session.
        """
        logging.info(f"Getting session for {self.config.database}")

        session = ORMUtils.get_sync_session(self.engine)()
        try:
            yield session
        finally:
            logging.info(f"Closing session for {self.config.database}")

            session.close()
