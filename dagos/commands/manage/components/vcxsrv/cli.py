import logging
import os
import platform
import shutil
import subprocess
from pathlib import Path

import click

from dagos.commands.manage.component_scanning import SoftwareComponent
from dagos.console import console
from dagos.exceptions.software_components import UnsupportedPlatformException
from dagos.utils.file_utils import download_file

# Ensure this software component is only available on Windows
if platform.system() != "Windows":
    raise UnsupportedPlatformException("VcXsrv only runs on Windows!")


@click.group(name="vcxsrv", chain=True)
def cli():
    """
    Install or configure VcXsrv.

    VcXsrv is an open-source X-server for Windows.
    Project home: https://sourceforge.net/projects/vcxsrv
    """
    pass


@cli.command()
@click.pass_context
def install(ctx: click.Context):
    """Install VcXsrv."""
    logging.info("Downloading the latest VcXsrv installer")
    file = download_file(
        "https://sourceforge.net/projects/vcxsrv/files/latest/download",
    )

    def cleanup():
        logging.debug("Removing installer")
        file.unlink()

    ctx.call_on_close(cleanup)

    logging.info("Running installer")
    logging.info("You may be prompted by Windows to give permission")
    with console.status("Installing VcXsrv ...", spinner="material"):
        result = subprocess.run([str(file), "/S"], shell=True, capture_output=True)

    if result.returncode == 0:
        logging.info("Successfully finished installation")
    else:
        errors = result.stderr.decode("utf-8")
        logging.error(f"Failed VcXsrv installation: {errors}")
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
