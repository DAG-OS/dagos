from __future__ import annotations

import typing as t

import click
import rich_click

from .commands import Command, CommandRegistry, CommandType


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
            CommandRegistry.add_command(
                CommandType.MANAGE, component.build_manage_command_group()
            )

        return component


class SoftwareComponent(object, metaclass=SoftwareComponentRegistry):
    """Base class for software components."""

    def __init__(self, name: str) -> None:
        self.name: str = name
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
                group.add_command(command.build(command.type.value))
        return group


class InstallIntelliJCommand(Command):
    """Install the IntelliJ IDE."""

    def __init__(self, parent: SoftwareComponent) -> None:
        super().__init__(CommandType.INSTALL, parent)

    def execute(self) -> None:
        print("Installing the idea")


class UninstallIntelliJCommand(Command):
    def __init__(self, parent: SoftwareComponent) -> None:
        super().__init__(CommandType.UNINSTALL, parent)


class IntelliJSoftwareComponent(SoftwareComponent):
    """Manage the IntelliJ IDE."""

    def __init__(self) -> None:
        super().__init__("idea")
        self.add_command(InstallIntelliJCommand(self))
        self.add_command(UninstallIntelliJCommand(self))


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
    IntelliJSoftwareComponent()

    group = click.Group("dagos")
    for command_group in CommandRegistry.commands.values():
        group.add_command(command_group)
    return group
