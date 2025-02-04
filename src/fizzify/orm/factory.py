from .config import ORMUrlBaseConfig
from .session.asyncio import AsyncSessionManager
from .session.sync import SyncSessionManager


class SessionFactory:
    def __init__(self, config: ORMUrlBaseConfig):
        self.config = config

    def get_sync_session_manager(self) -> SyncSessionManager:
        return SyncSessionManager(self.config)

    def get_async_session_manager(self) -> AsyncSessionManager:
        return AsyncSessionManager(self.config)
