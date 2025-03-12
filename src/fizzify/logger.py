from logging import Formatter, Handler, Logger

from typing_extensions import Self


class FizzifyLogger(Logger):
    def __init__(self, logger: Logger | str = __name__):
        self.logger = self.get_logger(logger)

        self._handler: Handler | None = None

    @classmethod
    def get_logger(cls, logger: Logger | str = __name__) -> Logger:
        if isinstance(logger, str):
            from logging import getLogger

            logger = getLogger(logger)

        return logger

    @property
    def handler(self) -> Handler:
        if self._handler is None:
            raise RuntimeError("No handler set")

        return self._handler

    @handler.setter
    def handler(self, handler: Handler):
        self._handler = handler

    def set_handler(self, handler: Handler) -> Self:
        self.logger.addHandler(handler)
        self._handler = handler

        return self

    def remove_handler(self) -> Self:
        self.logger.removeHandler(self.handler)
        self._handler = None

        return self

    def set_formatter(self, formatter: Formatter) -> Self:
        self.handler.setFormatter(formatter)

        return self

    def remove_formatter(self) -> Self:
        self.handler.setFormatter(None)

        return self

    def log(self, level: int, message: str):
        self.logger.log(level, message)

    def info(self, message: str):
        self.logger.info(message)

    def debug(self, message: str):
        self.logger.debug(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)

    def critical(self, message: str):
        self.logger.critical(message)

    def exception(self, message: str):
        self.logger.exception(message)
