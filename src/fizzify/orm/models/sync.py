import logging
from collections.abc import Sequence
from typing import Any, Literal

from sqlalchemy import UnaryExpression
from sqlalchemy.engine import Engine
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.orm import Session as SqlAlchemySession
from sqlalchemy.sql._typing import _DMLColumnArgument
from sqlalchemy.sql.roles import ExpressionElementRole
from typing_extensions import Self, override

from ...utils.orm import ORMUtils
from ..statement.options import (
    DeleteOptions,
    ExceptOptions,
    InsertOptions,
    SelectOptions,
    UpdateOptions,
)
from .base import Base


class SyncBase(Base):
    __abstract__ = True

    @classmethod
    @override
    def __create_table__(cls, engine: Engine) -> None:
        logging.info(f"Creating table for {cls.__name__}")

        cls.metadata.create_all(engine)

    @classmethod
    @override
    def __delete_table__(cls, engine: Engine) -> None:
        logging.info(f"Deleting table for {cls.__name__}")

        cls.metadata.drop_all(engine)

    @classmethod
    def _find(
        cls,
        session: SqlAlchemySession,
        filters: Sequence[ExpressionElementRole[bool]] | None = None,
    ) -> Sequence[Self]:
        stmt_generator = cls._get_statement_generator()
        stmt = stmt_generator.generate(
            model_class=cls,
            options=SelectOptions(filters=filters),
        )

        return session.execute(stmt).scalars().all()

    @classmethod
    def _update(
        cls,
        session: SqlAlchemySession,
        filters: Sequence[ExpressionElementRole[bool]],
        values: dict[_DMLColumnArgument, Any],
    ) -> Literal[True]:
        stmt_generator = cls._get_statement_generator()
        stmt = stmt_generator.generate(
            model_class=cls,
            options=UpdateOptions(mode="update", filters=filters, values=values),
        )

        session.execute(stmt)
        session.commit()

        return True

    def save(self, session: SqlAlchemySession) -> Self:
        try:
            logging.info(f"Saving {self.__class__.__name__}")
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
        filters: Sequence[ExpressionElementRole[bool]] | None = None,
    ) -> Self | None:
        logging.info(f"Finding one {cls.__name__}")

        results = cls._find(session, filters)

        return results[0] if results else None

    @classmethod
    @override
    def find_all(
        cls,
        session: SqlAlchemySession,
        filters: Sequence[ExpressionElementRole[bool]] | None = None,
    ) -> Sequence[Self]:
        logging.info(f"Finding all {cls.__name__}")

        return cls._find(session, filters)

    @classmethod
    @override
    def find_all_sorted(
        cls,
        session: SqlAlchemySession,
        order_by: Sequence[UnaryExpression],
        filters: Sequence[ExpressionElementRole[bool]] | None = None,
        limit: int | None = None,
    ) -> Sequence[Self]:
        stmt_generator = cls._get_statement_generator()
        stmt = stmt_generator.generate(
            model_class=cls,
            options=SelectOptions(
                mode="select_sorted", filters=filters, order_by=order_by
            ),
        ).limit(limit)

        if filters:
            stmt = stmt.filter(*filters)

        return session.execute(stmt).scalars().all()

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
        logging.info(
            f"Updating {cls.__name__} with filters: {filters} and values: {values}"
        )

        try:
            return cls._update(session, filters, values)
        except Exception as e:
            logging.error(f"Error updating {cls.__name__}: {e}")
            session.rollback()
            raise e

    @classmethod
    @override
    def delete_one(
        cls, session: SqlAlchemySession, filters: Sequence[ExpressionElementRole[bool]]
    ) -> Literal[True]:
        logging.info(f"Deleting one {cls.__name__}")

        try:
            stmt_generator = cls._get_statement_generator()
            stmt = stmt_generator.generate(
                model_class=cls,
                options=DeleteOptions(mode="delete", filters=filters),
            )
            session.execute(stmt)
            session.commit()

            return True
        except Exception as e:
            logging.error(f"Error deleting one {cls.__name__}: {e}")
            session.rollback()

            raise e

    def _insert_or_ignore_by_stmt(self, session: SqlAlchemySession) -> Literal[True]:
        stmt_generator = self.__class__._get_statement_generator()
        stmt = stmt_generator.generate(
            model_class=self.__class__,
            options=InsertOptions(
                mode="insert_or_ignore",
                values=ORMUtils.get_field_and_value(self),
                driver_name=ORMUtils.get_driver_name(session.bind.engine),  # type: ignore
            ),
        )
        session.execute(stmt)

        return True

    def _insert_or_ignore_not_support(
        self, session: SqlAlchemySession
    ) -> Literal[True]:
        unique_fields = ORMUtils.get_unique_constraint_fields(self.__class__)
        is_exists = self.find_one(
            session,
            filters=[
                getattr(self.__class__, field) == getattr(self, field)
                for field in unique_fields
            ],
        )
        if is_exists is None:
            self.save(session)

        return True

    @override
    def insert_or_ignore(self, session: SqlAlchemySession) -> Literal[True]:
        """
        Insert the object into the database if it doesn't exist, otherwise ignore it.

        Returns:
            bool: True if the insert or ignore was successful, False otherwise.
        """
        driver_name = ORMUtils.get_driver_name(session.bind.engine)  # type: ignore

        try:
            match driver_name:
                case "sqlite" | "postgresql":
                    self._insert_or_ignore_by_stmt(session)
                case _:
                    return self._insert_or_ignore_not_support(session)

            session.commit()

            return True
        except Exception as e:
            logging.error(f"Error inserting or ignoring {self.__class__.__name__}: {e}")
            session.rollback()

            raise e

    def _insert_or_update_by_stmt(self, session: SqlAlchemySession) -> Literal[True]:
        stmt_generator = self.__class__._get_statement_generator()
        stmt = stmt_generator.generate(
            model_class=self.__class__,
            options=InsertOptions(
                mode="insert_or_update",
                values=ORMUtils.get_field_and_value(self),
                driver_name=ORMUtils.get_driver_name(session.bind.engine),  # type: ignore
            ),
        )
        session.execute(stmt)

        return True

    def _insert_or_update_not_support(
        self, session: SqlAlchemySession
    ) -> Literal[True]:
        unique_fields = ORMUtils.get_unique_constraint_fields(self.__class__)
        is_exists = self.find_one(
            session,
            filters=[
                getattr(self.__class__, field) == getattr(self, field)
                for field in unique_fields
            ],
        )
        if is_exists is None:
            self.save(session)
        else:
            session.merge(self)

        return True

    @override
    def insert_or_update(self, session: SqlAlchemySession) -> Literal[True]:
        """
        Insert the object into the database if it doesn't exist, otherwise update it.

        Returns:
            bool: True if the insert or update was successful, False otherwise.
        """
        values = ORMUtils.get_field_and_value(self)

        if not values:
            raise ValueError(
                "The values dictionary must not be empty for insert_or_update."
            )

        driver_name = ORMUtils.get_driver_name(session.bind.engine)  # type: ignore

        try:
            match driver_name:
                case "sqlite" | "postgresql":
                    self._insert_or_update_by_stmt(session)
                case _:
                    return self._insert_or_update_not_support(session)

            session.commit()

            return True
        except Exception as e:
            logging.error(f"Error inserting or updating {self.__class__.__name__}: {e}")
            session.rollback()

            raise e

    @classmethod
    @override
    def get_except(
        cls,
        session: SqlAlchemySession,
        keys1: list[InstrumentedAttribute[Any]],
        keys2: list[InstrumentedAttribute[Any]],
        filters: Sequence[ExpressionElementRole[bool]] | None = None,
    ) -> Sequence[Self]:
        stmt_generator = cls._get_statement_generator()
        stmt = stmt_generator.generate(
            model_class=cls,
            options=ExceptOptions(keys1=keys1, keys2=keys2, filters=filters),
        )

        return session.execute(stmt).scalars().all()
