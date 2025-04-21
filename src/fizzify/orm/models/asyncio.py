import logging
from collections.abc import Sequence
from typing import Any, Literal

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.sql._typing import _DMLColumnArgument
from sqlalchemy.sql.roles import ExpressionElementRole
from typing_extensions import Self, override

from ..statement.options import (
    DeleteOptions,
    InsertOptions,
    SelectOptions,
    UpdateOptions,
)
from .base import Base


class AsyncBase(Base):
    __abstract__ = True

    @classmethod
    @override
    async def __create_table__(cls, engine: AsyncEngine) -> None:
        logging.info(f"Creating table for {cls.__name__}")

        async with engine.begin() as conn:
            await conn.run_sync(cls.metadata.create_all)

    @classmethod
    @override
    async def __delete_table__(cls, engine: AsyncEngine) -> None:
        logging.info(f"Deleting table for {cls.__name__}")
        async with engine.begin() as conn:
            await conn.run_sync(cls.metadata.drop_all)

    @classmethod
    async def _find(
        cls, session: AsyncSession, filters: Sequence[ExpressionElementRole[bool]]
    ) -> Sequence[Self]:
        logging.info(f"Finding {cls.__name__}")

        stmt_generator = cls._get_statement_generator()
        stmt = stmt_generator.generate(
            model_class=cls,
            options=SelectOptions(mode="select", filters=filters),
        )

        instance = await session.execute(stmt)

        return instance.scalars().all()

    @classmethod
    async def _update(
        cls,
        session: AsyncSession,
        filters: Sequence[ExpressionElementRole[bool]],
        values: dict[_DMLColumnArgument, Any],
    ) -> Literal[True]:
        stmt_generator = cls._get_statement_generator()
        stmt = stmt_generator.generate(
            model_class=cls,
            options=UpdateOptions(mode="update", filters=filters, values=values),
        )

        await session.execute(stmt)
        await session.commit()

        return True

    @override
    async def save(self, session: AsyncSession) -> Self:
        try:
            logging.info(f"Saving {self.__class__.__name__}")

            session.add(self)
            await session.commit()

        except Exception as e:
            await session.rollback()
            raise e

        return self

    @classmethod
    @override
    async def insert_many(
        cls, session: AsyncSession, objects: Sequence[Self]
    ) -> Literal[True]:
        logging.info(f"Inserting many {cls.__name__}")

        try:
            session.add_all(objects)
            await session.commit()

            return True
        except Exception as e:
            await session.rollback()
            raise e

    @classmethod
    @override
    async def fast_insert_many(
        cls, session: AsyncSession, objects: list[dict[str, Any]]
    ) -> Literal[True]:
        logging.info(f"Fast inserting many {cls.__name__}")

        try:
            from sqlalchemy import insert

            await session.execute(insert(cls).values(objects))
            await session.commit()

            return True
        except Exception as e:
            await session.rollback()
            raise e

    @override
    @classmethod
    async def find_one(
        cls, session: AsyncSession, filters: Sequence[ExpressionElementRole[bool]]
    ) -> Self | None:
        logging.info(f"Finding one {cls.__name__}")

        results = await cls._find(session, filters)

        return results[0] if results else None

    @override
    @classmethod
    async def find_all(
        cls, session: AsyncSession, filters: Sequence[ExpressionElementRole[bool]]
    ) -> Sequence[Self]:
        logging.info(f"Finding all {cls.__name__}")

        return await cls._find(session, filters)

    @override
    @classmethod
    async def update(
        cls,
        session: AsyncSession,
        filters: Sequence[ExpressionElementRole[bool]],
        values: dict[_DMLColumnArgument, Any],
    ) -> Literal[True]:
        logging.info(f"Updating {cls.__name__}")

        try:
            return await cls._update(session, filters, values)
        except Exception as e:
            await session.rollback()
            raise e

    @override
    @classmethod
    async def delete_one(
        cls,
        session: AsyncSession,
        filters: Sequence[ExpressionElementRole[bool]],
    ) -> Literal[True]:
        logging.info(f"Deleting one {cls.__name__}")

        try:
            stmt_generator = cls._get_statement_generator()
            stmt = stmt_generator.generate(
                model_class=cls,
                options=DeleteOptions(mode="delete", filters=filters),
            )
            await session.execute(stmt)
            await session.commit()

            return True
        except Exception as e:
            logging.error(f"Error deleting one {cls.__name__}: {e}")
            await session.rollback()
            raise e
