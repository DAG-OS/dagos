import typing as t
from io import StringIO

from dagos.exceptions import DagosException
from dagos.platform.exceptions import UnsupportedPlatformException


class NoSupportedContainerEngineException(UnsupportedPlatformException):
    """No supported container engine was found."""

    def __init__(self, supported_engines: t.List[str]) -> None:
        message = StringIO()
        engines = ", ".join(supported_engines)
        message.writelines(
            [
                "No supported container engine found!",
                f"Please install one of {engines} and try again.",
            ]
        )
        super.__init__(message.getvalue())


class ContainerException(DagosException):
    """During interaction with containers something went wrong."""
