from __future__ import annotations

import typing as t
from abc import abstractmethod
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


class CommandRegistry(type):
    """A metaclass responsible for registering constructed commands grouped by
    their type.
    """

    commands: t.Dict[CommandType, t.List[t.Union[click.Command, click.Group]]] = {}

    def __call__(cls, *args: t.Any, **kwds: t.Any) -> t.Any:
        """The registry hooks into the object construction lifecycle to register
        constructed commands. Only after their construction it is possible to
        access their type.
        """
        self = super().__call__(*args, **kwds)

        cls.add_command(self.type, self.build())

        return self

    @classmethod
    def add_command(
        cls,
        type: CommandType,
        command: t.Union[click.Command, click.Group],
    ) -> None:
        """Add provided command of provided type to the command registry.

        Args:
            type (CommandType): The command type.
            command (click.Command | click.Group): The command to register.
        """
        if not type.name in cls.commands:
            cls.commands[type.name] = click.Group(
                name=type.value,
                help=f"{type.value.capitalize()} software components.",
            )
        cls.commands[type.name].add_command(command)


class Command(metaclass=CommandRegistry):
    """Base class for software component commands."""

    def __init__(self, type: CommandType, parent: SoftwareComponent) -> None:  # type: ignore reportUndefinedVariable
        self.type: CommandType = type
        self.parent: SoftwareComponent = parent  # type: ignore

    def build(self, name: t.Optional[str] = None) -> click.Command:
        """Build a Click command for the CLI.

        Note: The command doc string is used as the help text for the command.
        If none is provided the command type and software component name are
        used to construct a generic help text.

        Args:
            name (str, optional): The name of the command. If none is provided,
            the command type is used as the name. Defaults to None.

        Returns:
            click.Command: A Click command to be used in a CLI.
        """
        # TODO: Allow overriding
        help_text = (
            self.__doc__
            if self.__doc__
            else f"{self.type.value.capitalize()} the {self.parent.name} software component."
        )
        name = self.parent.name if name == None else name
        return click.Command(name=name, help=help_text, callback=self.execute)

    @abstractmethod
    def execute(self) -> None:
        """Execute the command."""
        raise NotImplementedError()
