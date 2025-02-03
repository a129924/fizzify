from ..config import ORMUrlBaseConfig


class BaseManager:
    def __init__(self, config: ORMUrlBaseConfig):
        self.config = config

    def get_engine(self):
        raise NotImplementedError("This method should be overridden.")

    def get_session(self):
        raise NotImplementedError("This method should be overridden.")
