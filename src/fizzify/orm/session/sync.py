from collections.abc import Generator
from contextlib import contextmanager

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
        return ORMUtils.get_engine(self.config)

    @contextmanager
    @override
    def get_session(self) -> Generator[Session, None, None]:
        """
        Get the session for the synchronous session.
        """
        session = ORMUtils.get_sync_session(self.get_engine())()
        yield session
        session.close()
