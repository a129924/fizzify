from collections.abc import Sequence
from typing import Any, Literal

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.sql._typing import _DMLColumnArgument
from sqlalchemy.sql.roles import ExpressionElementRole
from typing_extensions import Self, override

from .base import Base


class AsyncBase(Base):
    __abstract__ = True

    @classmethod
    @override
    async def __create_table__(cls, engine: AsyncEngine) -> None:
        async with engine.begin() as conn:
            await conn.run_sync(cls.metadata.create_all)

    @classmethod
    async def _find(
        cls, session: AsyncSession, filters: Sequence[ExpressionElementRole[bool]]
    ) -> Sequence[Self]:
        instance = await session.execute(cls._generate_statement("select", filters))

        return instance.scalars().all()

    @classmethod
    async def _update(
        cls,
        session: AsyncSession,
        filters: Sequence[ExpressionElementRole[bool]],
        values: dict[_DMLColumnArgument, Any],
    ) -> Literal[True]:
        stmt = cls._generate_statement("update", filters, values)

        await session.execute(stmt)
        await session.commit()

        return True

    @override
    async def save(self, session: AsyncSession) -> Self:
        try:
            session.add(self)
            await session.commit()

        except Exception as e:
            await session.rollback()
            raise e

        return self

    @override
    async def find_one(
        cls, session: AsyncSession, filters: Sequence[ExpressionElementRole[bool]]
    ) -> Self | None:
        results = await cls._find(session, filters)

        return results[0] if results else None

    @override
    async def find_all(
        cls, session: AsyncSession, filters: Sequence[ExpressionElementRole[bool]]
    ) -> Sequence[Self]:
        return await cls._find(session, filters)

    @override
    async def update(
        cls,
        session: AsyncSession,
        filters: Sequence[ExpressionElementRole[bool]],
        values: dict[_DMLColumnArgument, Any],
    ) -> Literal[True]:
        try:
            return await cls._update(session, filters, values)
        except Exception as e:
            await session.rollback()
            raise e

    @override
    async def delete_one(
        cls,
        session: AsyncSession,
        filters: Sequence[ExpressionElementRole[bool]],
    ) -> Literal[True]:
        try:
            await session.execute(cls._generate_statement("delete", filters))
            await session.commit()

            return True
        except Exception as e:
            await session.rollback()
            raise e
