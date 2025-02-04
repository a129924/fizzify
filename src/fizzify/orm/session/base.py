from functools import cached_property

from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine

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
