import typing as t
from pathlib import Path

from .exceptions import SoftwareComponentScanException


class SoftwareComponent:
    """A representation of a software component."""

    name: str
    cli: t.Optional[Path]
    config: t.Optional[Path]
    actions: t.List[Path] = []

    def __init__(self, name: str) -> None:
        self.name = name

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
