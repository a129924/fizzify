from typing import Any, Generic, TypeVar, overload

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import Delete, Insert, Select, Update
from sqlalchemy.sql.selectable import CompoundSelect

from .options import (
    DeleteOptions,
    ExceptOptions,
    InsertOptions,
    SelectOptions,
    UpdateOptions,
)

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
                    index_elements=options.index_elements,
                )
            case "insert_or_update":
                return ORMUtils.generate_insert_or_update_stmt(
                    model_class,
                    options.values,
                    driver_name=options.driver_name,
                    index_elements=options.index_elements,
                )

    @classmethod
    def _generate_except_statement(
        cls,
        options: ExceptOptions,
    ) -> CompoundSelect[Any]:
        """
        Generate an except statement.

        Args:
            options: The options for the except statement.

        Returns:
            The except statement.
        """
        from sqlalchemy import except_, select

        query1 = select(*options.keys1)
        query2 = select(*options.keys2)

        if options.filters1 is not None:
            query1 = query1.filter(*options.filters1)

        if options.filters2 is not None:
            query2 = query2.filter(*options.filters2)

        return except_(query1, query2)

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
    @overload
    def generate(
        cls,
        model_class: type[ModelClass],
        options: ExceptOptions,
    ) -> CompoundSelect[Any]:
        """
        Generate an except statement.

        Args:
            model_class: The model class to except from.
            options: The options for the except statement.

        Returns:
            The except statement.
        """

    @classmethod
    def generate(
        cls,
        model_class: type[ModelClass],
        options: DeleteOptions
        | InsertOptions
        | SelectOptions
        | UpdateOptions
        | ExceptOptions,
    ) -> Select[Any] | Update | Delete | Insert | CompoundSelect[Any]:
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
            case ExceptOptions():
                return cls._generate_except_statement(options)
