from collections.abc import Sequence
from typing import Any, Literal, overload

from sqlalchemy import Engine, UnaryExpression
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
    @overload
    def _generate_statement(
        cls,
        mode: Literal["select"],
        filters: Sequence[ExpressionElementRole[bool]],
    ) -> Select[Any]: ...

    @classmethod
    @overload
    def _generate_statement(
        cls,
        mode: Literal["select_sorted"],
        order_by: Sequence[UnaryExpression],
        filters: Sequence[ExpressionElementRole[bool]] | None = None,
    ) -> Select[Any]: ...

    @classmethod
    @overload
    def _generate_statement(
        cls,
        mode: Literal["update"],
        filters: Sequence[ExpressionElementRole[bool]],
        values: dict[_DMLColumnArgument, Any],
    ) -> Update: ...

    @classmethod
    @overload
    def _generate_statement(
        cls,
        mode: Literal["delete"],
        filters: Sequence[ExpressionElementRole[bool]],
    ) -> Delete: ...

    @classmethod
    @overload
    def _generate_statement(
        cls,
        mode: Literal["insert_or_ignore"],
        driver_name: str,
        values: dict[_DMLColumnArgument, Any],
    ) -> Insert: ...

    @classmethod
    @overload
    def _generate_statement(
        cls,
        mode: Literal["insert_or_update"],
        driver_name: str,
        values: dict[_DMLColumnArgument, Any],
    ) -> Insert: ...

    @classmethod
    def _generate_statement(  # type: ignore
        cls,
        mode: Literal[
            "select",
            "update",
            "delete",
            "insert_or_ignore",
            "insert_or_update",
            "select_sorted",
        ],
        driver_name: str | None = None,
        filters: Sequence[ExpressionElementRole[bool]] | None = None,
        values: dict[_DMLColumnArgument, Any] | None = None,
        order_by: Sequence[UnaryExpression] | None = None,
    ) -> Select[Any] | Update | Delete | Insert:
        match mode:
            case "select" if filters is not None:
                from sqlalchemy import select

                return select(cls).filter(*filters)
            case "select_sorted" if order_by is not None:
                from sqlalchemy import select

                return select(cls).order_by(*order_by)
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

    @classmethod
    def get_except(
        cls,
        session: Session | AsyncSession,
        except_key1: str,
        cls2: type[Self],
        except_key2: str,
    ) -> Sequence[Self]:
        raise NotImplementedError("get_except should be overridden")
