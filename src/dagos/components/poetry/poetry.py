import subprocess
from pathlib import Path

from loguru import logger

import dagos.platform.utils as platform_utils
import dagos.utils.file_utils as file_utils
from dagos.core.commands import InstallCommand
from dagos.core.commands import UninstallCommand
from dagos.core.components import SoftwareComponent

# TODO: Remove limit to linux as this is only necessary because of hard coded adding to path
platform_utils.assert_linux()
platform_utils.assert_command_available("curl")
platform_utils.assert_command_available("python3")


class PoetrySoftwareComponent(SoftwareComponent):
    """
    Manage poetry, a Python dependency manager and build tool.

    Project home: <https://github.com/python-poetry/poetry>
    """

    def __init__(self) -> None:
        super().__init__("poetry")
        self.add_command(InstallPoetryCommand(self))
        self.add_command(UninstallPoetryCommand(self))


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

        logger.info("Add poetry to path")
        binary = Path.home() / ".local" / "bin" / "poetry"
        file_utils.create_symlink("/usr/local/bin/poetry", binary, force=True)


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

        logger.info("Remove poetry from path")
        Path("/usr/local/bin/poetry").unlink()
