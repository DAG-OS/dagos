import typing as t
from pathlib import Path

from .exceptions import SoftwareComponentScanException


class SoftwareComponent:
    """A representation of a software component."""

    name: str
    cli: None | Path
    config: None | Path
    actions: t.List[Path] = []

    def __init__(self, name: str) -> None:
        self.name = name

    def validate(self) -> None:
        """Check if the software component is valid.

        Raises:
            SoftwareComponentScanException: Raised if the component is invalid.
        """
        if not self.cli.exists() and len(self.actions) == 0:
            raise SoftwareComponentScanException(
                f"There is no CLI for '{self.name}' software component!"
            )
