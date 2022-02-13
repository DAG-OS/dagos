import typing as t
from abc import ABC

import click
import rich_click

from .commands import Command, CommandType, InstallCommand


class SoftwareComponent(ABC):
    pass


class SoftwareComponentManager(object):
    """Manages available software components."""

    def __init__(self) -> None:
        self.components = []

    def register(self, component: SoftwareComponent) -> None:
        """Register provided software component. Avoids registering duplicates.

        Args:
            component (SoftwareComponent): The software component to register.
        """
        if component not in self.components:
            self.components.append(component)

    def deregister(self, component: SoftwareComponent) -> None:
        """Deregisters proovided software component.

        Args:
            component (SoftwareComponent): The software component to deregister."
        """
        if component in self.components:
            self.components.remove(component)

    def build_command_groups(self) -> t.List[click.Group]:
        """Build Click groups for each command type.

        Returns:
            t.List[click.Group]: Click command groups sorted by type.
        """
        groups = []

        for type in CommandType:
            group = click.Group(
                name=type.value, help=f"{type.value.capitalize()} software components."
            )
            for component in self.components:
                if type == CommandType.MANAGE:
                    group.add_command(component.build_manage_command_group())
                elif not component.commands[type.name] == None:
                    group.add_command(component.get_command(type).build(component.name))
            if len(group.commands) > 0:
                groups.append(group)

        return groups


class SoftwareComponent(ABC):
    """Base class for software components."""

    def __init__(self, manager: SoftwareComponentManager, name: str) -> None:
        self.manager = manager
        self.manager.register(self)
        self.name = name
        self.commands = {}
        for type in CommandType:
            self.commands[type.name] = None

    def add_command(self, command: Command) -> None:
        """Add provided command to this software component.

        Args:
            command (Command): The command to add.
        """
        self.commands[command.type.name] = command

    def get_command(self, type: CommandType) -> t.Optional[Command]:
        """Get command by provided type.

        Args:
            type (CommandType): The command type to look for.

        Returns:
            t.Optional[Command]: The found command or None if there is no such
            command.
        """
        if self.commands[type.name] != None:
            return self.commands[type.name]
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
                group.add_command(command.build())
        return group


class InstallIntelliJCommand(InstallCommand):
    """Install the IntelliJ IDE."""

    def execute(self) -> None:
        print("Installing the idea")


class IntelliJSoftwareComponent(SoftwareComponent):
    """Manage the IntelliJ IDE."""

    def __init__(self, manager: SoftwareComponentManager) -> None:
        super().__init__(manager, "idea")
        self.add_command(InstallIntelliJCommand())


rich_click.core.COMMAND_GROUPS = {
    "dagos": [
        {
            "name": "Software Component Commands",
            "commands": [type.value for type in CommandType],
        },
    ]
}
rich_click.core.COMMANDS_PANEL_TITLE = "General Commands"


def test():
    manager = SoftwareComponentManager()
    IntelliJSoftwareComponent(manager)

    group = click.Group("dagos")
    for command_group in manager.build_command_groups():
        group.add_command(command_group)
    return group
