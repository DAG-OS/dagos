import logging
from contextlib import contextmanager

from rich.console import Console

console = Console()


@contextmanager
def spinner(message: str, success_message: str = "", log_level: int = logging.INFO):
    """Display a spinner with provided text during long-running operations.

    Args:
        message (str): The message to show while spinning.
        success_message (str, optional): An optional success message. Defaults to "".
        log_level (int, optional): The log level to use for the success message. Defaults to logging.INFO.
    """
    with console.status(message, spinner="material"):
        yield
        if success_message:
            logging.log(log_level, success_message)
