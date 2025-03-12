from logging import Handler, LogRecord

from ...orm.session.asyncio import AsyncSessionManager
from ...orm.session.sync import SyncSessionManager


class ORMLogBaseHandler(Handler):
    def __init__(self, session_manager: SyncSessionManager | AsyncSessionManager):
        super().__init__()

        self.session_manager = session_manager
        self.__init_table__()

    def __init_table__(self):
        raise NotImplementedError("Subclass must implement ‘__init_table__’")

    def emit(self, record: LogRecord):
        raise NotImplementedError("Subclass must implement ‘emit’")
