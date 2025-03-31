from typing import Any, Generic, TypeVar, overload

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import Delete, Insert, Select, Update

from .options import DeleteOptions, InsertOptions, SelectOptions, UpdateOptions

ModelClass = TypeVar("ModelClass", bound=DeclarativeBase)


class StatementGenerator(Generic[ModelClass]):
    @classmethod
    def _generate_select_statement(
        cls,
        model_class: type[ModelClass],
        options: SelectOptions,
    ) -> Select[Any]:
        """
        Generate a select statement.

        Args:
            model_class: The model class to select from.
            options: The options for the select statement.

        Returns:
            The select statement.
        """
        from sqlalchemy import select

        stmt = select(*(options.select_columns or [model_class]))

        if options.filters is not None:
            stmt = stmt.filter(*options.filters)

        if options.order_by is not None:
            stmt = stmt.order_by(*options.order_by)

        return stmt

    @classmethod
    def _generate_update_statement(
        cls,
        model_class: type[ModelClass],
        options: UpdateOptions,
    ) -> Update:
        """
        Generate an update statement.

        Args:
            model_class: The model class to update.
            options: The options for the update statement.

        Returns:
            The update statement.
        """
        from sqlalchemy import update

        return update(model_class).filter(*options.filters).values(options.values)

    @classmethod
    def _generate_delete_statement(
        cls,
        model_class: type[ModelClass],
        options: DeleteOptions,
    ) -> Delete:
        """
        Generate a delete statement.

        Args:
            model_class: The model class to delete from.
            options: The options for the delete statement.

        Returns:
            The delete statement.
        """
        from sqlalchemy import delete

        return delete(model_class).filter(*options.filters)

    @classmethod
    def _generate_insert_statement(
        cls,
        model_class: type[ModelClass],
        options: InsertOptions,
    ) -> Insert:
        """
        Generate an insert statement.

        Args:
            model_class: The model class to insert into.
            options: The options for the insert statement.

        Returns:
            The insert statement.
        """
        from ...utils.orm import ORMUtils

        match options.mode:
            case "insert_or_ignore":
                return ORMUtils.generate_insert_or_ignore_stmt(
                    model_class,
                    options.values,
                    driver_name=options.driver_name,
                )
            case "insert_or_update":
                return ORMUtils.generate_insert_or_update_stmt(
                    model_class,
                    options.values,
                    driver_name=options.driver_name,
                )

    @classmethod
    @overload
    def generate(
        cls,
        model_class: type[ModelClass],
        options: DeleteOptions,
    ) -> Delete:
        """
        Generate a delete statement.

        Args:
            model_class: The model class to delete from.
            options: The options for the delete statement.

        Returns:
            The delete statement.
        """

    @classmethod
    @overload
    def generate(
        cls,
        model_class: type[ModelClass],
        options: InsertOptions,
    ) -> Insert:
        """
        Generate an insert statement.

        Args:
            model_class: The model class to insert into.
            options: The options for the insert statement.

        Returns:
            The insert statement.
        """

    @classmethod
    @overload
    def generate(
        cls,
        model_class: type[ModelClass],
        options: SelectOptions,
    ) -> Select[Any]:
        """
        Generate a select statement.

        Args:
            model_class: The model class to select from.
            options: The options for the select statement.

        Returns:
            The select statement.
        """

    @classmethod
    @overload
    def generate(
        cls,
        model_class: type[ModelClass],
        options: UpdateOptions,
    ) -> Update:
        """
        Generate an update statement.

        Args:
            model_class: The model class to update.
            options: The options for the update statement.

        Returns:
            The update statement.
        """

    @classmethod
    def generate(
        cls,
        model_class: type[ModelClass],
        options: DeleteOptions | InsertOptions | SelectOptions | UpdateOptions,
    ) -> Select[Any] | Update | Delete | Insert:
        """
        Generate a statement.

        Args:
            model_class: The model class to generate the statement for.
            options: The options for the statement.

        Returns:
            The generated statement.
        """
        match options:
            case DeleteOptions():
                return cls._generate_delete_statement(model_class, options)
            case InsertOptions():
                return cls._generate_insert_statement(model_class, options)
            case SelectOptions():
                return cls._generate_select_statement(model_class, options)
            case UpdateOptions():
                return cls._generate_update_statement(model_class, options)
