import logging
import os
import shutil
from pathlib import Path

import click

from dagos.commands.manage.component_scanning import SoftwareComponent
from dagos.console import console
from dagos.platform.utils import assert_command_available, assert_windows
from dagos.utils import powershell_utils

assert_windows()
assert_command_available("choco")


@click.group(name="vcxsrv", chain=True)
def cli():
    """
    Install or configure VcXsrv.

    VcXsrv is an open-source X-server for Windows.
    Project home: https://sourceforge.net/projects/vcxsrv
    """
    pass


@cli.command()
@click.option(
    "--attended",
    is_flag=True,
    default=False,
    help="Pause after installation is done.",
)
def install(attended: bool):
    """Install VcXsrv."""
    with console.status("Installing VcXsrv ...", spinner="material"):
        result = powershell_utils.run_as_admin("choco install vcxsrv --yes", attended)
    if result.returncode == 0:
        logging.info("Successfully finished installation")
    else:
        logging.error("Failed VcXsrv installation")
        exit(1)


@cli.command()
@click.pass_context
def configure(ctx: click.Context):
    """Configure VcXsrv to autostart with Windows."""
    current_user = os.getlogin()
    auto_start = Path(
        f"C:/Users/{current_user}/AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup"
    )
    if not auto_start.exists():
        logging.error("Unable to find autostart directory!")
        exit(1)

    component: SoftwareComponent = ctx.obj
    # TODO: Allow providing a configuration file via component configuration
    xlaunch_config = component.cli.parent / "config.xlaunch"
    if not xlaunch_config.exists():
        logging.error("There is no configuration file present for VcXsrv!")
        exit(1)

    logging.info("Configuring VcXsrv to start on Windows startup")
    auto_xlaunch_config = auto_start / "config.xlaunch"
    shutil.copyfile(xlaunch_config, auto_xlaunch_config)

    logging.info(f"Run the X-server by running '{auto_xlaunch_config}'")
