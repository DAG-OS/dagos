import typing as t
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path

import click

from .exceptions import SoftwareComponentScanException


class ActionType(Enum):
    INSTALL = "install"


# TODO: Action provider?
# TODO: Default installation dir?
class Action(ABC):
    type: ActionType

    @staticmethod
    @abstractmethod
    def parse_action(path: Path):
        pass

    @abstractmethod
    def execute_action(self) -> None:
        pass

    @abstractmethod
    def get_click_command(self) -> click.Command:
        pass


class SoftwareComponent:
    """A representation of a software component."""

    name: str
    folders: t.List[Path]
    cli: t.Optional[Path]
    config: t.Optional[Path]
    actions: t.List[Action]

    def __init__(self, name: str) -> None:
        self.name = name
        self.folders = []
        self.actions = []

    def has_cli(self) -> bool:
        if hasattr(self, "cli"):
            return self.cli.exists()
        return False

    def has_actions(self) -> bool:
        return True if len(self.actions) > 0 else False

    def validate(self) -> None:
        """Check if the software component is valid.

        Raises:
            SoftwareComponentScanException: Raised if the component is invalid.
        """
        cli_is_valid = True if hasattr(self, "cli") and self.cli.exists() else False
        has_actions = True if len(self.actions) > 0 else False

        if not cli_is_valid and not has_actions:
            raise SoftwareComponentScanException(
                f"{self.name}: There is neither a valid CLI nor actions!"
            )
