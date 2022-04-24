from __future__ import annotations

import typing as t
from abc import abstractmethod
from enum import Enum

import click

from dagos.platform import PlatformIssue
from dagos.platform import UnsupportedPlatformException


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
        command = super().__call__(*args, **kwds)

        cls.add_command(command.type, command.build())

        return command

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
        if type.name not in cls.commands:
            cls.commands[type.name] = click.Group(
                name=type.value,
                help=f"{type.value.capitalize()} software components.",
            )
        cls.commands[type.name].add_command(command)


def _build_unsupported_platform_command(
    name: str, platform_issues: t.List[PlatformIssue]
) -> click.Command:
    help_text = "[dim]:latin_cross: "
    if len(platform_issues) == 1:
        help_text += platform_issues[0].description
    else:
        help_text += f"There are {len(platform_issues)} platform issues[/]"

    def callback(*args, **kwargs):
        fixable_issues = [x for x in platform_issues if x.fixable]
        unfixable_issues = [x for x in platform_issues if not x.fixable]
        message = f"The '{name}' command does not support the current platform!\nThere is a total of {len(platform_issues)} issues."
        if len(unfixable_issues) > 0:
            message += f" Since there are {len(unfixable_issues)} unfixable issues this is irrecoverable!"
            message += "\n\nUnfixable issues:"
            index = 1
            for issue in unfixable_issues:
                message += f"\n\t{index}. {issue.description}"
                index += 1
        if len(fixable_issues) > 0:
            message += "\n\nFixable issues:"
            index = 1
            for issue in fixable_issues:
                message += f"\n\t{index}. {issue.description}"
                if issue.fix_instructions:
                    message += f"\n\t   Try: {issue.fix_instructions}"
                index += 1

        raise UnsupportedPlatformException(message)

    return click.Command(name=name, help=help_text, callback=callback)


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
        name = self.parent.name if name is None else name
        # TODO: Allow overriding
        help_text = (
            self.__doc__
            if self.__doc__
            else f"{self.type.value.capitalize()} the {self.parent.name} software component."
        )

        # TODO: Allow command specific platform issues? e.g. root privileges?
        platform_issues = self.parent.supports_platform()
        if len(platform_issues) > 0:
            # TODO: Check if all issues are fixable
            return _build_unsupported_platform_command(name, platform_issues)

        return click.Command(name=name, help=help_text, callback=self.execute)

    @abstractmethod
    def execute(self, *args) -> None:
        """Execute the command."""
        raise NotImplementedError()


class InstallCommand(Command):
    """Base class for install commands."""

    def __init__(self, parent: SoftwareComponent) -> None:  # type: ignore reportUndefinedVariable
        super().__init__(CommandType.INSTALL, parent)


class UninstallCommand(Command):
    """Base class for uninstall commands."""

    def __init__(self, parent: SoftwareComponent) -> None:  # type: ignore reportUndefinedVariable
        super().__init__(CommandType.UNINSTALL, parent)


class UpdateCommand(Command):
    """Base class for update commands."""

    def __init__(self, parent: SoftwareComponent) -> None:  # type: ignore reportUndefinedVariable
        super().__init__(CommandType.UPDATE, parent)


class ConfigureCommand(Command):
    """Base class for configure commands."""

    def __init__(self, parent: SoftwareComponent) -> None:  # type: ignore reportUndefinedVariable
        super().__init__(CommandType.CONFIGURE, parent)


class VerifyCommand(Command):
    """Base class for verify commands."""

    def __init__(self, parent: SoftwareComponent) -> None:  # type: ignore reportUndefinedVariable
        super().__init__(CommandType.VERIFY, parent)
