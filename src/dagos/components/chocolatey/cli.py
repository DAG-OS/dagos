import typing as t
from pathlib import Path

import click
from loguru import logger

from dagos.core.commands import InstallCommand
from dagos.core.components import SoftwareComponent
from dagos.platform import platform_utils
from dagos.utils import powershell_utils

platform_utils.assert_windows()


class ChocolateySoftwareComponent(SoftwareComponent):
    """
    Manage Chocolatey.

    Chocolatey is a package manager for Windows.

    Project home: <https://chocolatey.org/>
    """

    def __init__(self) -> None:
        super().__init__("chocolatey")


class InstallChocolateyCommand(InstallCommand):
    """Install Chocolatey via PowerShell."""

    def __init__(self, parent: SoftwareComponent) -> None:
        super().__init__(parent)

    def build(self, name: t.Optional[str] = None) -> click.Command:
        command = super().build(name)
        attended_option = click.Option(
            ["--attended"],
            is_flag=True,
            default=False,
            help="Pause after installation is done.",
        )
        command.params.append(attended_option)
        return command

    def execute(self, attended: bool) -> None:
        install_script = Path(__file__).parent / "install.ps1"

        result = powershell_utils.run_as_admin(str(install_script), attended)

        if result.returncode == 0:
            logger.info("Successfully installed Chocolatey")
        else:
            logger.error("Failed Chocolatey installation")
            exit(1)
