from .config import ORMEngineConfig, ORMUrlBaseConfig
from .session.asyncio import AsyncSessionManager
from .session.sync import SyncSessionManager


class SessionFactory:
    def __init__(
        self,
        config: ORMUrlBaseConfig,
        engine_config: ORMEngineConfig,
    ):
        self.config = config
        self.engine_config = engine_config

    def get_sync_session_manager(self) -> SyncSessionManager:
        return SyncSessionManager(self.config, self.engine_config)

    def get_async_session_manager(self) -> AsyncSessionManager:
        return AsyncSessionManager(self.config, self.engine_config)
