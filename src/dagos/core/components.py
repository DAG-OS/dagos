from __future__ import annotations

import typing as t
from pathlib import Path

import click
from loguru import logger

from dagos.exceptions import SoftwareComponentScanException

from .commands import Command, CommandType


class SoftwareComponentRegistry(type):
    """A metaclass responsible for registering constructed software components."""

    components: t.List[SoftwareComponent] = []

    def __call__(cls, *args: t.Any, **kwds: t.Any) -> t.Any:
        """The registry hooks into the object construction lifecycle to register
        constructed software components. It also registers the manage command
        group to the command registry.
        """
        component = super().__call__(*args, **kwds)

        if not cls in cls.components:
            cls.components.append(component)

        return component

    @classmethod
    def find_component(cls, name: str) -> t.Optional[SoftwareComponent]:
        for component in cls.components:
            if component.name == name:
                return component
        return None


class SoftwareComponent(object, metaclass=SoftwareComponentRegistry):
    """Base class for software components."""

    name: str
    folders: t.List[Path]
    files: t.List[Path]
    commands: t.Dict[str, Command]

    def __init__(
        self, name: str, folders: t.List[Path] = None, files: t.List[Path] = None
    ) -> None:
        self.name = name
        self.commands = {}
        for type in CommandType:
            self.commands[type.name] = None
        self.folders = folders if folders else []
        self.files = files if files else []

    def add_command(self, command: Command, force: t.Optional[bool] = False) -> None:
        """Add provided command to this software component.

        Args:
            command (Command): The command to add.
            force (t.Optional[bool]) If True, overrides any existing commands of the same type. Defaults, to False.
        """
        if not self.commands[command.type.name] is None and not force:
            if force:
                logger.debug(
                    f"Overwriting the existing '{command.type.name}' command on '{self.name}' component"
                )
            else:
                logger.trace(
                    f"The '{self.name}' component already has a '{command.type.name}' command"
                )
                return
        self.commands[command.type.name] = command

    def get_file(self, file_pattern: str) -> t.Optional[Path]:
        """Try to find a file that matches the provided pattern. The first match
        or None, if there is no match, is returned.

        Args:
            file_pattern (str): A pattern to match a file against.

        Returns:
            t.Optional[Path]: The first matched file or None.
        """
        for file in self.files:
            if file.match(file_pattern):
                return file
        return None

    def build_manage_command_group(self) -> click.Group:
        """Aggregate all commands into a 'manage' command group.

        Returns:
            click.Group: A Click group containing all commands for this software
            component.
        """
        help_text = (
            self.__class__.__doc__
            if self.__class__.__doc__
            else f"Manage the {self.name} software component."
        )
        group = click.Group(name=self.name, help=help_text)
        for command in self.commands.values():
            if not command == None:
                group.add_command(command.build(command.type.value))
        return group

    def validate(self) -> None:
        if hasattr(self, "cli"):
            cli_is_valid = self.cli.exists()
        else:
            cli_is_valid = False
        if not cli_is_valid:
            raise SoftwareComponentScanException(
                f"{self.name}: There is neither a valid CLI nor actions!"
            )
