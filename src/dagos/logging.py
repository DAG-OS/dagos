import logging
import typing as t
from contextlib import contextmanager
from enum import Enum

from loguru import logger
from rich.console import Console
from rich.logging import RichHandler
from rich.theme import Theme


class LogLevel(Enum):
    TRACE = 5
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    SUCCESS = 25
    WARNING = logging.WARNING
    ERROR = logging.ERROR


logging.addLevelName(LogLevel.TRACE.value, LogLevel.TRACE.name)
logging.addLevelName(LogLevel.SUCCESS.value, LogLevel.SUCCESS.name)

console = Console(
    theme=Theme(
        {
            "logging.level.trace": "gray42",
            "logging.level.debug": "white",
            "logging.level.info": "bright_blue",
            "logging.level.success": "green",
            "logging.level.warning": "orange1",
            "logging.level.error": "red",
        }
    )
)


def configure_logging(verbosity: int) -> None:
    log_format = "{message}"
    date_format = "%Y-%m-%d %H:%M:%S"

    log_show_path = False
    log_show_time = False
    if verbosity == 0:
        log_level = LogLevel.INFO
    elif verbosity == 1:
        log_level = LogLevel.DEBUG
    else:
        log_level = LogLevel.TRACE
        log_show_path = True

    handler = RichHandler(
        console=console,
        rich_tracebacks=True,
        show_path=log_show_path,
        show_time=log_show_time,
        log_time_format=date_format,
        markup=True,
    )

    logger.remove()
    # Use function to format log to avoid duplicate exception logging
    # See: https://github.com/Delgan/loguru/issues/592
    logger.add(handler, format=lambda _: log_format, level=log_level.name)


@contextmanager
def spinner(
    message: str,
    success_message: str = "",
    log_level: t.Union[str, LogLevel] = LogLevel.INFO,
):
    """Display a spinner with provided text during long-running operations.

    Args:
        message (str): The message to show while spinning.
        success_message (str, optional): An optional success message. Defaults to "".
        log_level (str | LogLevel, optional): The log level to use for the success message. Defaults to INFO.
    """
    with console.status(message, spinner="material"):
        yield
        if success_message:
            logger.log(
                log_level if isinstance(log_level, str) else log_level.name,
                success_message,
            )
