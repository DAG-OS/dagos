import logging
import os
import shutil
import typing as t
from distutils.command.build import build
from pathlib import Path

import click

import dagos.platform.utils as platform_utils
from dagos.console import spinner
from dagos.core.commands import Command, CommandType
from dagos.core.components import SoftwareComponent
from dagos.utils import powershell_utils

platform_utils.assert_windows()
platform_utils.assert_command_available("choco")


class VcXsrvSoftwareComponent(SoftwareComponent):
    """Install or configure VcXsrv.

    VcXsrv is an open-source X-server for Windows.
    Project home: https://sourceforge.net/projects/vcxsrv
    """

    def __init__(self) -> None:
        super().__init__("vcxsrv")
        self.add_command(InstallVcXsrvCommand(self))
        self.add_command(ConfigureVcXsrvCommand(self))


class InstallVcXsrvCommand(Command):
    """Install VcXsrv."""

    def __init__(self, parent: SoftwareComponent) -> None:
        super().__init__(CommandType.INSTALL, parent)

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
        with spinner("Installing VcXsrv ..."):
            result = powershell_utils.run_as_admin(
                "choco install vcxsrv --yes", attended
            )
            if result.returncode == 0:
                logging.info("Successfully finished installation")
            else:
                logging.error("Failed VcXsrv installation")
                exit(1)


class ConfigureVcXsrvCommand(Command):
    """Configure VcXsrv to autostart with Windows."""

    def __init__(self, parent: SoftwareComponent) -> None:
        super().__init__(CommandType.CONFIGURE, parent)

    def execute(self) -> None:
        current_user = os.getlogin()
        auto_start = Path(
            f"C:/Users/{current_user}/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup"
        )
        if not auto_start.exists():
            logging.error("Unable to find autostart directory!")
            exit(1)

        # TODO: Allow providing a configuration file via component configuration
        xlaunch_config = Path(__file__).parent / "config.xlaunch"
        if not xlaunch_config.exists():
            logging.error("There is no configuration file present for VcXsrv!")
            exit(1)

        logging.info("Configuring VcXsrv to start on Windows startup")
        auto_xlaunch_config = auto_start / "config.xlaunch"
        shutil.copyfile(xlaunch_config, auto_xlaunch_config)

        logging.info(f"Run the X-server by running '{auto_xlaunch_config}'")
