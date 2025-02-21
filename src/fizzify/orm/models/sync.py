import logging
from collections.abc import Sequence
from typing import Any, Literal

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session as SqlAlchemySession
from sqlalchemy.sql._typing import _DMLColumnArgument
from sqlalchemy.sql.roles import ExpressionElementRole
from typing_extensions import Self, override

from ...utils.orm import ORMUtils
from .base import Base


class SyncBase(Base):
    __abstract__ = True

    @classmethod
    @override
    def __create_table__(cls, engine: Engine) -> None:
        logging.info(f"Creating table for {cls.__name__}")

        cls.metadata.create_all(engine)

    @classmethod
    def _find(
        cls, session: SqlAlchemySession, filters: Sequence[ExpressionElementRole[bool]]
    ) -> Sequence[Self]:
        stmt = cls._generate_statement("select", filters=filters)

        return session.execute(stmt).scalars().all()

    @classmethod
    def _update(
        cls,
        session: SqlAlchemySession,
        filters: Sequence[ExpressionElementRole[bool]],
        values: dict[_DMLColumnArgument, Any],
    ) -> Literal[True]:
        stmt = cls._generate_statement("update", filters=filters, values=values)

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
        filters: Sequence[ExpressionElementRole[bool]],
    ) -> Self | None:
        logging.info(f"Finding one {cls.__name__}")

        results = cls._find(session, filters)

        return results[0] if results else None

    @classmethod
    @override
    def find_all(
        cls,
        session: SqlAlchemySession,
        filters: Sequence[ExpressionElementRole[bool]],
    ) -> Sequence[Self]:
        logging.info(f"Finding all {cls.__name__}")

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
        logging.info(f"Updating {cls.__name__}")

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
            session.execute(cls._generate_statement("delete", filters=filters))
            session.commit()

            return True
        except Exception as e:
            logging.error(f"Error deleting one {cls.__name__}: {e}")
            session.rollback()

            raise e

    @override
    def insert_or_ignore(self, session: SqlAlchemySession) -> Literal[True]:
        """
        Insert the object into the database if it doesn't exist, otherwise ignore it.

        Returns:
            bool: True if the insert or ignore was successful, False otherwise.
        """
        try:
            session.execute(
                self._generate_statement(
                    "insert_or_ignore",
                    values=ORMUtils.get_field_and_value(self),
                    driver_name=ORMUtils.get_driver_name(session.bind.engine),  # type: ignore
                )
            )
            session.commit()

            return True
        except Exception as e:
            logging.error(f"Error inserting or ignoring {self.__class__.__name__}: {e}")
            session.rollback()

            raise e
