from collections.abc import Sequence
from typing import Any, Literal

from sqlalchemy import Engine
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.orm import Session as SqlAlchemySession
from sqlalchemy.sql._typing import _DMLColumnArgument
from sqlalchemy.sql.roles import ExpressionElementRole
from sqlalchemy.types import Integer
from typing_extensions import Self


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id})"

    @classmethod
    def __create_table__(cls, engine: Engine) -> None:
        cls.metadata.create_all(engine)

    @classmethod
    def _find(
        cls, session: SqlAlchemySession, filters: Sequence[ExpressionElementRole[bool]]
    ) -> Sequence[Self]:
        from sqlalchemy import select

        stmt = select(cls).filter(*filters)

        return session.execute(stmt).scalars().all()

    @classmethod
    def _update(
        cls,
        session: SqlAlchemySession,
        filters: Sequence[ExpressionElementRole[bool]],
        values: dict[_DMLColumnArgument, Any],
    ) -> Literal[True]:
        from sqlalchemy import update

        stmt = update(cls).filter(*filters).values(values)

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
    def find_one(
        cls, session: SqlAlchemySession, filters: Sequence[ExpressionElementRole[bool]]
    ) -> Self | None:
        results = cls._find(session, filters)

        return results[0] if results else None

    @classmethod
    def find_all(
        cls, session: SqlAlchemySession, filters: Sequence[ExpressionElementRole[bool]]
    ) -> Sequence[Self]:
        return cls._find(session, filters)

    @classmethod
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
    def delete_one(
        cls, session: SqlAlchemySession, filters: Sequence[ExpressionElementRole[bool]]
    ) -> Literal[True]:
        try:
            session.delete(cls.find_one(session, filters))
            session.commit()

            return True
        except Exception as e:
            session.rollback()
            raise e
