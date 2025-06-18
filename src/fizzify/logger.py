from enum import IntEnum
from logging import Filter, Formatter, Handler, Logger
from typing import Any

from typing_extensions import Self


class Level(IntEnum):
    INFO = 20
    ERROR = 40
    DEBUG = 10
    CRITICAL = 50
    WARNING = 30
    NOTSET = 0


class FizzifyLogger(Logger):
    def __init__(self, logger: Logger | str = __name__):
        self.logger = self.get_logger(logger)

        self._handler: Handler | None = None
        self._handlers: list[Handler] = []

    @classmethod
    def get_logger(cls, logger: Logger | str = __name__) -> Logger:
        if isinstance(logger, str):
            from logging import getLogger

            logger = getLogger(logger)

        return logger

    @property
    def handler(self) -> Handler:
        if not self._handlers:
            raise RuntimeError("No handler set")

        return self._handlers[-1]

    @handler.setter
    def handler(self, handler: Handler):
        self._handlers.append(handler)

    def set_handler(self, handler: Handler) -> Self:
        self.logger.addHandler(handler)
        self._handlers.append(handler)

        return self

    def remove_handler(self) -> Self:
        self.logger.removeHandler(self.handler)
        self._handlers.pop()

        return self

    def set_formatter(self, formatter: Formatter) -> Self:
        self.handler.setFormatter(formatter)

        return self

    def remove_formatter(self) -> Self:
        self.handler.setFormatter(None)

        return self

    def set_filter(self, filter: Filter) -> Self:
        self.handler.addFilter(filter)

        return self

    def remove_filter(self) -> Self:
        self.handler.removeFilter(self.handler.filters[-1])

        return self

    def set_level(self, level: Level) -> Self:
        self.logger.setLevel(level)

        return self

    def log(
        self,
        level: Level,
        message: str,
        extra: dict[str, Any] | None = None,
    ):
        self.logger.log(level, message, extra=extra)

    def info(
        self,
        message: str,
        extra: dict[str, Any] | None = None,
    ):
        self.logger.info(message, extra=extra)

    def debug(
        self,
        message: str,
        extra: dict[str, Any] | None = None,
    ):
        self.logger.debug(message, extra=extra)

    def warning(
        self,
        message: str,
        extra: dict[str, Any] | None = None,
    ):
        self.logger.warning(message, extra=extra)

    def error(
        self,
        message: str,
        extra: dict[str, Any] | None = None,
    ):
        self.logger.error(message, extra=extra)

    def critical(
        self,
        message: str,
        extra: dict[str, Any] | None = None,
    ):
        self.logger.critical(message, extra=extra)

    def exception(
        self,
        message: str,
        extra: dict[str, Any] | None = None,
    ):
        self.logger.exception(message, extra=extra)
