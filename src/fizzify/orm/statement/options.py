from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal

from sqlalchemy import UnaryExpression
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.sql._typing import _DMLColumnArgument
from sqlalchemy.sql.roles import ExpressionElementRole


@dataclass
class BaseOptions:
    mode: Literal[
        "select",
        "select_sorted",
        "update",
        "delete",
        "insert_or_ignore",
        "insert_or_update",
        "except",
    ]


@dataclass
class InsertOptions:  # CREATE
    values: dict[_DMLColumnArgument, Any]
    mode: Literal["insert_or_ignore", "insert_or_update"] = "insert_or_ignore"
    driver_name: Literal["sqlite", "postgresql", "mysql"] = "sqlite"


@dataclass
class SelectOptions:  # READ
    mode: Literal["select", "select_sorted"] = "select"
    select_columns: Sequence[InstrumentedAttribute[Any]] | None = None
    filters: Sequence[ExpressionElementRole[bool]] | None = None
    order_by: Sequence[UnaryExpression] | None = None


@dataclass
class UpdateOptions:  # UPDATE
    filters: Sequence[ExpressionElementRole[bool]]
    values: dict[_DMLColumnArgument, Any]
    mode: Literal["update"] = "update"


@dataclass
class DeleteOptions:  # DELETE
    filters: Sequence[ExpressionElementRole[bool]]
    mode: Literal["delete"] = "delete"


@dataclass
class ExceptOptions:
    keys1: Sequence[InstrumentedAttribute[Any]]
    keys2: Sequence[InstrumentedAttribute[Any]]
    mode: Literal["except"] = "except"
