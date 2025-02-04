from collections.abc import Sequence
from typing import Any, Literal

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session as SqlAlchemySession
from sqlalchemy.sql._typing import _DMLColumnArgument
from sqlalchemy.sql.roles import ExpressionElementRole
from typing_extensions import Self, override

from .base import Base


class SyncBase(Base):
    __abstract__ = True

    @classmethod
    @override
    def __create_table__(cls, engine: Engine) -> None:
        cls.metadata.create_all(engine)

    @classmethod
    def _find(
        cls, session: SqlAlchemySession, filters: Sequence[ExpressionElementRole[bool]]
    ) -> Sequence[Self]:
        stmt = cls._generate_statement("select", filters)

        return session.execute(stmt).scalars().all()

    @classmethod
    def _update(
        cls,
        session: SqlAlchemySession,
        filters: Sequence[ExpressionElementRole[bool]],
        values: dict[_DMLColumnArgument, Any],
    ) -> Literal[True]:
        stmt = cls._generate_statement("update", filters, values)

        session.execute(stmt)
        session.commit()

        return True

    def save(self, session: SqlAlchemySession) -> Self:
        try:
            session.add(self)
            session.commit()

        except Exception as e:
            session.rollback()
            raise e

        return self

    @classmethod
    @override
    def find_one(
        cls,
        session: SqlAlchemySession,
        filters: Sequence[ExpressionElementRole[bool]],
    ) -> Self | None:
        results = cls._find(session, filters)

        return results[0] if results else None

    @classmethod
    @override
    def find_all(
        cls,
        session: SqlAlchemySession,
        filters: Sequence[ExpressionElementRole[bool]],
    ) -> Sequence[Self]:
        return cls._find(session, filters)

    @classmethod
    @override
    def update(
        cls,
        session: SqlAlchemySession,
        filters: Sequence[ExpressionElementRole[bool]],
        values: dict[_DMLColumnArgument, Any],
    ) -> Literal[True]:
        """
        Update the database with the given filters and values.

        Returns:
            bool: True if the update was successful, False otherwise.
        """
        try:
            return cls._update(session, filters, values)
        except Exception as e:
            session.rollback()

            raise e

    @classmethod
    @override
    def delete_one(
        cls, session: SqlAlchemySession, filters: Sequence[ExpressionElementRole[bool]]
    ) -> Literal[True]:
        try:
            session.execute(cls._generate_statement("delete", filters))
            session.commit()

            return True
        except Exception as e:
            session.rollback()
            raise e
