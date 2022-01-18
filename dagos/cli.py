import click
import logging

from . import __version__
from dagos.commands.manage.group import manage
from dagos.commands.wsl.group import wsl
from rich.logging import RichHandler


@click.group()
@click.option(
    "--verbose", "-v", is_flag=True, default=False, help="Enter verbose mode."
)
@click.version_option(
    prog_name="dagos",
    version=__version__,
    message="%(prog)s version %(version)s",
)
def dagos(verbose):
    log_format = "{message}"
    date_format = "%Y-%m-%d %H:%M:%S"
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format=log_format,
        datefmt=date_format,
        style="{",
        handlers=[RichHandler(rich_tracebacks=True)],
    )


dagos.add_command(manage)
dagos.add_command(wsl)
