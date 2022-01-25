import logging

import click

import dagos.platform.utils as platform_utils
from dagos.components.domain import SoftwareComponent
from dagos.utils import powershell_utils

platform_utils.assert_windows()


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
    "--attended",
    is_flag=True,
    default=False,
    help="Pause after installation is done.",
)
@click.pass_context
def install(ctx: click.Context, attended: bool):
    """Install Chocolatey via PowerShell."""
    component: SoftwareComponent = ctx.obj
    install_script = component.cli.parent / "install.ps1"

    result = powershell_utils.run_as_admin(str(install_script), attended)

    if result.returncode == 0:
        logging.info("Successfully installed Chocolatey")
    else:
        logging.error("Failed Chocolatey installation")
        exit(1)
