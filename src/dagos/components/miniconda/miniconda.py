import subprocess
import typing as t
from pathlib import Path

from loguru import logger

import dagos.utils.file_utils as file_utils
from dagos.core.commands import InstallCommand
from dagos.core.components import SoftwareComponent
from dagos.platform import OperatingSystem
from dagos.platform import PlatformIssue
from dagos.platform import PlatformSupportChecker


class MinicondaSoftwareComponent(SoftwareComponent):
    """
    Manage miniconda, a minimal installer for conda.

    Project home: <https://docs.conda.io/en/latest/miniconda.html>
    """

    def __init__(self) -> None:
        super().__init__("miniconda")
        self.add_command(InstallMinicondaCommand(self))

    def supports_platform(self) -> t.List[PlatformIssue]:
        return (
            PlatformSupportChecker()
            .check_operating_system([OperatingSystem.LINUX])
            .check_command_is_available("sh")
            .issues
        )


class InstallMinicondaCommand(InstallCommand):
    """Install miniconda."""

    def __init__(self, parent: SoftwareComponent) -> None:
        super().__init__(parent)

    def execute(self) -> None:
        logger.info("Download miniconda installer")
        installer_file = file_utils.download_file(
            "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
        )

        logger.info("Execute installer")
        # TODO: Allow configuring the install dir
        install_dir = Path.home() / "miniconda"
        subprocess.run(["sh", str(installer_file), "-b", "-p", str(install_dir)])

        logger.info("Remove installer")
        installer_file.unlink()

        logger.info("Add conda to path")
        binary = install_dir / "bin" / "conda"
        file_utils.create_symlink("/usr/local/bin/conda", binary, force=True)
