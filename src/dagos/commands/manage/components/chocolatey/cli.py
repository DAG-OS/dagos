import logging
import subprocess
from io import StringIO

import click

from dagos.commands.manage.component_scanning import SoftwareComponent
from dagos.platform.domain import OperatingSystem
from dagos.platform.utils import assert_windows

assert_windows()


@click.group(name="chocolatey", chain=True)
def cli():
    """
    Manage Chocolatey.

    Chocolatey is a package manager for Windows.
    Project home: https://chocolatey.org/
    """
    pass


@cli.command()
@click.option(
    "--unattended",
    is_flag=True,
    default=False,
    help="Run installation with minimal user interaction.",
)
@click.pass_context
def install(ctx: click.Context, unattended: bool):
    """Install Chocolatey via PowerShell."""
    component: SoftwareComponent = ctx.obj
    install_script = component.cli.parent / "install.ps1"

    logging.debug("Building PowerShell command")
    # TODO: Find a way to retrieve output from the started process
    command = StringIO()
    command.write(
        "powershell Start-Process powershell -Verb runAs -Wait -ArgumentList '"
    )
    command.write(str(install_script))
    if not unattended:
        command.write(";pause")
    command.write("'")

    logging.debug(f"Running command: {command}")
    logging.info("The installation requires administrator privileges")
    logging.info("Windows may prompt you for permission")
    result = subprocess.run(command.getvalue(), shell=True)

    if result.returncode == 0:
        logging.info("Successfully installed Chocolatey")
    else:
        logging.error("Failed Chocolatey installation")
        exit(1)
