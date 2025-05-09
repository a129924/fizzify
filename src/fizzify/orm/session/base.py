from functools import cached_property
from typing import Literal

from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.pool.impl import QueuePool

from ..config import ORMEngineConfig, ORMUrlBaseConfig


class BaseManager:
    def __init__(self, config: ORMUrlBaseConfig, engine_config: ORMEngineConfig):
        self.config = config
        self.engine_config = engine_config

    def get_engine(self):
        raise NotImplementedError("This method should be overridden.")

    @cached_property
    def engine(self) -> Engine | AsyncEngine:
        raise NotImplementedError("This property should be overridden.")

    def get_session(self):
        raise NotImplementedError("This method should be overridden.")

    def create_session(self):
        raise NotImplementedError("This method should be overridden.")

    def close_session(self):
        raise NotImplementedError("This method should be overridden.")

    @cached_property
    def pool(self) -> QueuePool:
        return self.engine.pool  # type: ignore

    def is_all_finished(self) -> bool:
        return self.pool.checkedout() == 0

    def wait_all_finished(self) -> Literal[True]:
        raise NotImplementedError("This method should be overridden.")

    def close(self, force: bool = False):
        raise NotImplementedError("This method should be overridden.")
