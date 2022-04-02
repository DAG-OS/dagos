import platform
import typing as t
from io import StringIO

from .domain import OperatingSystem
from dagos.exceptions import DagosException


class UnsupportedPlatformException(DagosException):
    """The current platform is unsupported."""


class UnsupportedOperatingSystem(UnsupportedPlatformException):
    """The current operating system is unsupported."""

    def __init__(self, supported_systems: t.List[OperatingSystem] = None):
        """Raise when the current operating system is not supported.

        Args:
            supported_platforms (t.List[OperatingSystem], optional): A list of supported platforms. Defaults to None.
        """
        self.current_system = platform.system()
        self.supported_systems = supported_systems

        message = StringIO()
        message.write(self.current_system)
        message.write(" is not supported")
        if supported_systems != None:
            if len(supported_systems) == 1:
                message.write(f", only {supported_systems[0].value} is")
            else:
                message.write(", only one of ")
                message.write(", ".join(x.value for x in supported_systems))
                message.write(" is")
        message.write("!")
        super().__init__(message.getvalue())
