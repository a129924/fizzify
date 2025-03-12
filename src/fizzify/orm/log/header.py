from logging import Handler, LogRecord

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session


class ORMLogBaseHandler(Handler):
    def __init__(self, session: Session | AsyncSession):
        super().__init__()

        self.session = session
        self.__init_table__()

    def __init_table__(self):
        raise NotImplementedError("Subclass must implement ‘__init_table__’")

    def emit(self, record: LogRecord):
        raise NotImplementedError("Subclass must implement ‘emit’")
