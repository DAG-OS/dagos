from __future__ import annotations

import textwrap
import typing as t
from pathlib import Path

import click
from loguru import logger
from rich.console import Group
from rich.console import group
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from .commands import Command
from .commands import CommandType
from dagos.platform import PlatformIssue


class SoftwareComponentRegistry(type):
    """A metaclass responsible for registering constructed software components."""

    components: t.List[SoftwareComponent] = []

    def __call__(cls, *args: t.Any, **kwds: t.Any) -> t.Any:
        """The registry hooks into the object construction lifecycle to register
        constructed software components.
        """
        component = super().__call__(*args, **kwds)

        if cls not in cls.components:
            cls.components.append(component)

        return component

    @classmethod
    def find_component(cls, name: str) -> t.Optional[SoftwareComponent]:
        for component in cls.components:
            if component.name == name:
                return component
        return None


class SoftwareComponent(metaclass=SoftwareComponentRegistry):
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
        if self.commands[command.type.name] is not None:
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
            if command != None:
                group.add_command(command.build(command.type.value))
        return group

    def supports_platform(self) -> t.List[PlatformIssue]:
        """Implementing commands may override this function to check if the current
        platform is supported. If there are any issues with running on this platform
        a list of issues should be returned.

        Typical checks:
        * Is the operating system supported?
        * Is all required software installed and available?
        * Are any environment variables missing?
        * Does the calling user have root privileges?

        Returns:
            t.List[PlatformValidationFinding]: Any issues found during the validation. If none are returned the platform is considered as supported.
        """
        return []

    def is_valid(self) -> bool:
        is_valid = False
        # TODO: Improve component validation
        if len(self.commands) > 0:
            is_valid = True
        return is_valid

    def __rich__(self) -> Panel:
        @group()
        def get_renderables():
            yield Markdown(f"{textwrap.dedent(self.__doc__)}")
            yield ""

            command_table = Table(title="Commands", show_header=False, box=None)
            command_table.add_column("Type")
            command_table.add_column("Description")

            for command in [x for x in self.commands.values() if x]:
                command_table.add_row(command.type.value, command.__doc__)
            yield command_table
            yield ""

            file_tree = Tree("files")
            for file in self.files:
                file_tree.add(str(file))
            yield file_tree

        return Panel(
            Group(get_renderables()),
            title=f"Component: {self.name}",
            title_align="left",
        )
