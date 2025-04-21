from collections.abc import Sequence
from functools import cached_property
from typing import Any, Literal

from sqlalchemy import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy.sql._typing import _DMLColumnArgument
from sqlalchemy.sql.roles import ExpressionElementRole
from typing_extensions import Self

from ..statement.generator import StatementGenerator


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls._convert_class_name_to_table_name()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}"

    @classmethod
    def __create_table__(cls, engine: Engine | AsyncEngine) -> None:
        raise NotImplementedError("__create_table__ should be overridden")

    @classmethod
    def __delete_table__(cls, engine: Engine | AsyncEngine) -> None:
        raise NotImplementedError("__delete_table__ should be overridden")

    @classmethod
    def _convert_class_name_to_table_name(cls) -> str:
        from re import sub

        return sub(r"(?<!^)(?=[A-Z])", "_", cls.__name__).lower()

    @classmethod
    def _get_statement_generator(cls) -> type[StatementGenerator[Self]]:
        return StatementGenerator[Self]

    @cached_property
    def conflict_fields(self) -> set[str]:
        from sqlalchemy import inspect

        from ...utils.orm import ORMUtils

        class_ = self.__class__

        return {
            column.name
            for column in inspect(class_).columns
            if column.primary_key is True or column.unique is True
        } | set(ORMUtils.get_unique_constraint_fields(class_))

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

    @classmethod
    def find_all_sorted(
        cls,
        session: Session | AsyncSession,
        order_by: Sequence[ExpressionElementRole[bool]],
        filters: Sequence[ExpressionElementRole[bool]] | None = None,
    ) -> Sequence[Self]:
        raise NotImplementedError("find_all_sorted should be overridden")

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

    def insert_or_ignore(
        self,
        session: Session | AsyncSession,
    ) -> Literal[True]:
        raise NotImplementedError("insert_or_ignore should be overridden")

    def insert_or_update(
        self,
        session: Session | AsyncSession,
    ) -> Literal[True]:
        raise NotImplementedError("insert_or_update should be overridden")

    @classmethod
    def get_except(
        cls,
        session: Session | AsyncSession,
        except_key1: str,
        cls2: type[Self],
        except_key2: str,
    ) -> Sequence[Self]:
        raise NotImplementedError("get_except should be overridden")
