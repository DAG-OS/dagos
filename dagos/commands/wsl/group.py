import click

from dagos.commands.wsl.import_wsl_distro import import_wsl_distro
from dagos.commands.wsl.prepare_wsl_distro import prepare_wsl_distro


@click.group(no_args_is_help=True)
def wsl():
    """
    Prepare or import WSL distros.
    """
    pass


wsl.add_command(import_wsl_distro)
wsl.add_command(prepare_wsl_distro)
