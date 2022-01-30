import typing as t
from pathlib import Path

from dagos.actions.domain import Action

from .exceptions import SoftwareComponentScanException


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
