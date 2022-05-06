from enum import Enum
from typing import List
from typing import Optional

from .platform_messages import build_unsupported_system_message


class OperatingSystem(Enum):
    WINDOWS = "Windows"
    LINUX = "Linux"


class PlatformScope(Enum):
    USER = "user"
    SYSTEM = "system"


class PlatformIssue:
    description: str
    """
    A human readable description of the issue.
    The string may contain Rich console markup. See https://rich.readthedocs.io/en/stable/markup.html
    """
    fixable: bool
    """Is the issue fixable?"""
    fix_instructions: Optional[str] = None
    """
    How to fix the issue?
    The string may contain Rich console markup. See https://rich.readthedocs.io/en/stable/markup.html
    """

    def __init__(
        self, description: str, fixable: bool, fix_instructions: Optional[str] = None
    ) -> None:
        self.description = description
        self.fixable = fixable
        self.fix_instructions = fix_instructions


class UnsupportedOperatingSystemIssue(PlatformIssue):
    def __init__(self, supported_operating_systems: List[OperatingSystem]) -> None:
        super().__init__(
            build_unsupported_system_message(supported_operating_systems), False
        )


class CommandNotAvailableIssue(PlatformIssue):
    def __init__(
        self,
        command: str,
        fixable: bool = True,
        installation_instructions: Optional[str] = None,
    ) -> None:
        super().__init__(
            f"Required command '{command}' is unavailable!",
            fixable,
            installation_instructions,
        )
