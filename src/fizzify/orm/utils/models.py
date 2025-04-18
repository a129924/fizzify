from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine

from fizzify.orm.models.asyncio import AsyncBase
from fizzify.orm.models.sync import SyncBase


def sync_create_tables(engine: Engine, tables: list[type[SyncBase]]) -> None:
    for table in tables:
        table.__create_table__(engine)


async def async_create_tables(
    engine: AsyncEngine, tables: list[type[AsyncBase]]
) -> None:
    for table in tables:
        await table.__create_table__(engine)
