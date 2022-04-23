from dataclasses import dataclass
from enum import Enum


class OperatingSystem(Enum):
    WINDOWS = "Windows"
    LINUX = "Linux"


@dataclass
class PlatformIssue:
    # TODO: Is the issue mitigatable? E.g. install certain command?
    description: str
    """A human readable description of the issue."""
