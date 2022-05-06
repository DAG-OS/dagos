import subprocess
import typing as t

from loguru import logger

from dagos.core.commands import InstallCommand
from dagos.core.commands import UninstallCommand
from dagos.core.components import SoftwareComponent
from dagos.platform import OperatingSystem
from dagos.platform import PlatformIssue
from dagos.platform import PlatformSupportChecker


class PoetrySoftwareComponent(SoftwareComponent):
    """
    Manage poetry, a Python dependency manager and build tool.

    Project home: <https://github.com/python-poetry/poetry>
    """

    def __init__(self) -> None:
        super().__init__("poetry")
        self.add_command(InstallPoetryCommand(self))
        self.add_command(UninstallPoetryCommand(self))

    def supports_platform(self) -> t.List[PlatformIssue]:
        # TODO: Remove limit to linux? Path doesn't need to be hard coded and curl doesn't have to be used
        return (
            PlatformSupportChecker()
            .check_operating_system([OperatingSystem.LINUX])
            .check_command_is_available("curl")
            .check_command_is_available("python3")
            .issues
        )


class InstallPoetryCommand(InstallCommand):
    """Install poetry."""

    def __init__(self, parent: SoftwareComponent) -> None:
        super().__init__(parent)

    def execute(self) -> None:
        logger.info("Download and run installer")
        subprocess.run(
            f"curl -sSL https://install.python-poetry.org | python3 -",
            shell=True,
        )


class UninstallPoetryCommand(UninstallCommand):
    """Uninstall poetry."""

    def __init__(self, parent: SoftwareComponent) -> None:
        super().__init__(parent)

    def execute(self) -> None:
        logger.info("Download and run uninstaller")
        subprocess.runn(
            f"curl -sSL https://install.python-poetry.org | python3 - --uninstall",
            shell=True,
        )
