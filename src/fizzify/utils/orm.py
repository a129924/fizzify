from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session as SqlAlchemySession
from sqlalchemy.orm import sessionmaker

from ..orm.config import ORMEngineConfig, ORMUrlBaseConfig


class ORMUtils:
    @classmethod
    def get_engine(
        cls,
        config: ORMUrlBaseConfig,
        engine_config: ORMEngineConfig,
    ) -> Engine:
        return create_engine(
            config.generate_url(),
            **engine_config.model_dump(exclude_none=True),
        )

    @classmethod
    def get_async_engine(
        cls,
        config: ORMUrlBaseConfig,
        engine_config: ORMEngineConfig,
    ) -> AsyncEngine:
        return create_async_engine(
            config.generate_url(),
            **engine_config.model_dump(exclude_none=True),
        )

    @classmethod
    def get_sync_session(cls, engine: Engine) -> sessionmaker[SqlAlchemySession]:
        return sessionmaker(bind=engine)

    @classmethod
    def get_async_session(cls, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(bind=engine, class_=AsyncSession)
