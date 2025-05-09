import logging
from collections.abc import Generator
from contextlib import contextmanager
from functools import cached_property
from typing import Literal

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

        session = self.create_session()
        try:
            yield session
        finally:
            logging.info(f"Closing session for {self.config.database}")

            self.close_session(session)

    @override
    def create_session(self) -> Session:
        """
        Create a new session.
        """
        return ORMUtils.get_sync_session(self.engine)()

    @override
    def close_session(self, session: Session):
        """
        Close the session.
        """
        session.close()

    @override
    def wait_all_finished(self) -> Literal[True]:
        """
        Wait for all sessions to finish.
        """
        from time import sleep

        while not self.is_all_finished():
            sleep(0.1)

        return True

    @override
    def close(self, force: bool = False):
        """
        Close the engine.
        """
        if force:
            self.wait_all_finished()

        self.engine.dispose()
