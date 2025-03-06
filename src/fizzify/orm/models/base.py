from collections.abc import Sequence
from typing import Any, Literal

from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.sql import Delete, Insert, Select, Update
from sqlalchemy.sql._typing import _DMLColumnArgument
from sqlalchemy.sql.roles import ExpressionElementRole
from typing_extensions import Self

from ...utils.orm import ORMUtils


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"

    @classmethod
    def __create_table__(cls, engine: Engine | AsyncEngine) -> None:
        raise NotImplementedError("__create_table__ should be overridden")

    @classmethod
    def _generate_statement(
        cls,
        mode: Literal[
            "select", "update", "delete", "insert_or_ignore", "insert_or_update"
        ],
        driver_name: str | None = None,
        filters: Sequence[ExpressionElementRole[bool]] | None = None,
        values: dict[_DMLColumnArgument, Any] | None = None,
    ) -> Select | Update | Delete | Insert:
        match mode:
            case "select" if filters is not None:
                from sqlalchemy import select

                return select(cls).filter(*filters)
            case "update" if values is not None and filters is not None:
                from sqlalchemy import update

                return update(cls).filter(*filters).values(values)
            case "delete" if filters is not None:
                from sqlalchemy import delete

                return delete(cls).filter(*filters)
            case "insert_or_ignore" if values is not None and driver_name is not None:
                return ORMUtils.generate_insert_or_ignore_stmt(
                    cls,
                    values,
                    driver_name=driver_name,
                )

            case "insert_or_update" if values is not None and driver_name is not None:
                return ORMUtils.generate_insert_or_update_stmt(
                    cls,
                    values,
                    driver_name=driver_name,
                )
            case _:
                raise ValueError(f"Invalid mode: {mode} or values: {values}")

    @classmethod
    def find_one(
        cls,
        session: Session | AsyncSession,
        filters: Sequence[ExpressionElementRole[bool]],
    ) -> Self | None:
        raise NotImplementedError("find should be overridden")

    @classmethod
    def find_all(
        cls,
        session: Session | AsyncSession,
        filters: Sequence[ExpressionElementRole[bool]],
    ) -> Sequence[Self]:
        raise NotImplementedError("find_all should be overridden")

    def save(self, session: Session | AsyncSession) -> Self:
        raise NotImplementedError("save should be overridden")

    @classmethod
    def update(
        cls,
        session: Session | AsyncSession,
        filters: Sequence[ExpressionElementRole[bool]],
        values: dict[_DMLColumnArgument, Any],
    ) -> Literal[True]:
        raise NotImplementedError("update should be overridden")

    @classmethod
    def delete_one(
        cls,
        session: Session | AsyncSession,
        filters: Sequence[ExpressionElementRole[bool]],
    ) -> Literal[True]:
        raise NotImplementedError("delete_one should be, overridden")

    @classmethod
    def insert_or_ignore(
        cls,
        session: Session | AsyncSession,
        values: dict[_DMLColumnArgument, Any],
    ) -> Literal[True]:
        raise NotImplementedError("insert_or_ignore should be overridden")

    @classmethod
    def insert_or_update(
        cls,
        session: Session | AsyncSession,
        values: dict[_DMLColumnArgument, Any],
    ) -> Literal[True]:
        raise NotImplementedError("insert_or_update should be overridden")
