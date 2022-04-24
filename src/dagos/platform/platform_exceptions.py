import typing as t

from .platform_domain import OperatingSystem
from .platform_messages import build_unsupported_system_message
from dagos.exceptions import DagosException


class UnsupportedPlatformException(DagosException):
    """The current platform is unsupported."""


class UnsupportedOperatingSystemException(UnsupportedPlatformException):
    """The current operating system is unsupported."""

    def __init__(self, supported_systems: t.List[OperatingSystem] = None):
        """Raise when the current operating system is not supported.

        Args:
            supported_platforms (t.List[OperatingSystem], optional): A list of supported platforms. Defaults to None.
        """
        self.supported_systems = supported_systems

        super().__init__(build_unsupported_system_message(supported_systems))
