from dagos.core.commands import Command
from dagos.core.commands import CommandType
from dagos.core.components import SoftwareComponent


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
