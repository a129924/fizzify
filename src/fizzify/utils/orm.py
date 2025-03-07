from typing import Any

from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.orm import Session as SqlAlchemySession
from sqlalchemy.sql._typing import _DMLColumnArgument
from sqlalchemy.sql.dml import Insert

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

    @classmethod
    def get_driver_name(cls, engine: Engine | AsyncEngine) -> str:
        """
        Get the driver name from the engine.

        Args:
            engine: The engine to get the driver name from.

        Returns:
            The driver name from the engine.
        For Example:
            * mssql+pyodbc -> mssql
            * postgresql -> postgresql
            * sqlite -> sqlite
        """
        return engine.url.drivername.split("+", 1)[0]

    @classmethod
    def get_unique_constraint_fields(cls, model: type[DeclarativeBase]) -> list[str]:
        if hasattr(model, "__table_args__") is False:
            return []

        from sqlalchemy import UniqueConstraint

        table_args = model.__table_args__

        for arg in table_args:
            if isinstance(arg, UniqueConstraint):
                return [column.name for column in arg.columns]

        return []

    @classmethod
    def get_field_and_value(
        cls, model: DeclarativeBase
    ) -> dict[_DMLColumnArgument, Any]:
        return {
            column.name: getattr(model, column.name)
            for column in model.__table__.columns
        }

    @classmethod
    def generate_insert_or_ignore_stmt(
        cls,
        model: type[DeclarativeBase],
        values: dict[_DMLColumnArgument, Any],
        driver_name: str,
    ) -> Insert:
        from sqlalchemy import insert

        match driver_name:
            case "sqlite":
                return insert(model).values(values).prefix_with("OR IGNORE")

            case "postgresql":
                return insert(model).values(
                    index_elements=ORMUtils.get_unique_constraint_fields(model)
                )
            case _:
                raise ValueError(f"Unsupported database: {driver_name}")

    @classmethod
    def generate_insert_or_update_stmt(
        cls,
        model: type[DeclarativeBase],
        values: dict[_DMLColumnArgument, Any],
        driver_name: str,
    ) -> Insert:
        match driver_name:
            case "sqlite":
                from sqlalchemy.dialects.sqlite import insert

                stmt = insert(model).values(values)
                return stmt.on_conflict_do_update(  # type: ignore
                    index_elements=ORMUtils.get_unique_constraint_fields(model),
                    set_=values,
                )

            case "postgresql":
                from sqlalchemy.dialects.postgresql import insert

                stmt = insert(model).values()
                return stmt.on_conflict_do_update(  # type: ignore
                    index_elements=ORMUtils.get_unique_constraint_fields(model)
                )

            case _:
                raise ValueError(f"Unsupported database: {driver_name}")
