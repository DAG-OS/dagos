import typing as t
from abc import ABC, abstractmethod
from enum import Enum

import click


class CommandType(Enum):
    """The supported commands for software components."""

    MANAGE = "manage"
    INSTALL = "install"
    UNINSTALL = "uninstall"
    UPDATE = "update"
    CONFIGURE = "configure"
    VERIFY = "verify"


class Command(ABC):
    """Base class for commands."""

    def __init__(self, type: CommandType) -> None:
        self.type = type

    def build(self, name: t.Optional[str] = None) -> click.Command:
        """Build a Click command for the CLI.

        Note: The command doc string is used as the help text for the command.

        Args:
            name (str, optional): The name of the command. If none is provided,
            the command type is used as the name. Defaults to None.

        Returns:
            click.Command: A Click command to be used in a CLI.
        """
        help_text = self.__doc__
        name = self.type.value if name == None else name
        return click.Command(name=name, help=help_text, callback=self.execute)

    @abstractmethod
    def execute(self) -> None:
        """Execute the command."""
        raise NotImplementedError()


class InstallCommand(Command):
    """Base class for commands with the INSTALL type."""

    def __init__(self) -> None:
        super().__init__(CommandType.INSTALL)
