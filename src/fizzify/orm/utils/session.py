from fizzify.orm.config import ORMEngineConfig, ORMUrlBaseConfig
from fizzify.orm.factory import SessionFactory
from fizzify.orm.session.asyncio import AsyncSessionManager
from fizzify.orm.session.sync import SyncSessionManager


def generate_session_factory(
    config: ORMUrlBaseConfig,
    engine_config: ORMEngineConfig,
) -> SessionFactory:
    return SessionFactory(config=config, engine_config=engine_config)


def generate_async_session_manager(
    config: ORMUrlBaseConfig,
    engine_config: ORMEngineConfig,
) -> AsyncSessionManager:
    return generate_session_factory(config, engine_config).get_async_session_manager()


def generate_sync_session_manager(
    config: ORMUrlBaseConfig,
    engine_config: ORMEngineConfig,
) -> SyncSessionManager:
    return generate_session_factory(config, engine_config).get_sync_session_manager()
