import logging

from rich.logging import RichHandler

from .console import console


def configure_logging(verbosity: int) -> None:
    log_format = "{message}"
    date_format = "%Y-%m-%d %H:%M:%S"
    add_logging_level("TRACE", logging.DEBUG - 5)

    log_show_path = False
    log_show_time = False
    if verbosity == 0:
        log_level = logging.INFO
    elif verbosity == 1:
        log_level = logging.DEBUG
    else:
        log_level = logging.TRACE
        log_show_path = True

    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        style="{",
        handlers=[
            RichHandler(
                console=console,
                rich_tracebacks=True,
                show_path=log_show_path,
                show_time=log_show_time,
            )
        ],
    )


# This function was taken from https://stackoverflow.com/a/35804945 and slightly modified.
def add_logging_level(level_name, level_num, method_name=None) -> None:
    """
    Comprehensively adds a new logging level to the `logging` module and the
    currently configured logging class.

    `levelName` becomes an attribute of the `logging` module with the value
    `levelNum`. `methodName` becomes a convenience method for both `logging`
    itself and the class returned by `logging.getLoggerClass()` (usually just
    `logging.Logger`). If `methodName` is not specified, `levelName.lower()` is
    used.

    To avoid accidental clobberings of existing attributes, this method will
    raise an `AttributeError` if the level name is already an attribute of the
    `logging` module or if the method name is already present

    Example
    -------
    >>> addLoggingLevel('TRACE', logging.DEBUG - 5)
    >>> logging.getLogger(__name__).setLevel("TRACE")
    >>> logging.getLogger(__name__).trace('that worked')
    >>> logging.trace('so did this')
    >>> logging.TRACE
    5

    """
    if not method_name:
        method_name = level_name.lower()

    if hasattr(logging, level_name):
        raise AttributeError("{} already defined in logging module".format(level_name))
    if hasattr(logging, method_name):
        raise AttributeError("{} already defined in logging module".format(method_name))
    if hasattr(logging.getLoggerClass(), method_name):
        raise AttributeError("{} already defined in logger class".format(method_name))

    # This method was inspired by the answers to Stack Overflow post
    # http://stackoverflow.com/q/2183233/2988730, especially
    # http://stackoverflow.com/a/13638084/2988730
    def log_for_level(self, message, *args, **kwargs):
        if self.isEnabledFor(level_num):
            self._log(level_num, message, args, **kwargs)

    def log_to_root(message, *args, **kwargs):
        logging.log(level_num, message, *args, **kwargs)

    logging.addLevelName(level_num, level_name)
    setattr(logging, level_name, level_num)
    setattr(logging.getLoggerClass(), method_name, log_for_level)
    setattr(logging, method_name, log_to_root)
