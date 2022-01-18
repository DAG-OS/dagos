import logging
import time

import click
from rich.logging import RichHandler

from dagos.commands.manage.cli import manage
from dagos.commands.wsl.cli import wsl

from . import __version__


def timer_callback(ctx: click.Context, param: click.Option, value: bool) -> None:
    if not value or ctx.resilient_parsing:
        return
    start = time.perf_counter()

    def print_elapsed_time():
        stop = time.perf_counter()
        logging.info(f"Elapsed time: {stop-start:0.3f} seconds")

    ctx.call_on_close(print_elapsed_time)


@click.group()
@click.option(
    "--verbose", "-v", is_flag=True, default=False, help="Enter verbose mode."
)
@click.version_option(
    prog_name="dagos",
    version=__version__,
    message="%(prog)s version %(version)s",
)
@click.option(
    "--timer/--no-timer",
    default=True,
    help="Print execution time upon completion.",
    callback=timer_callback,
)
def dagos(verbose: bool, timer: bool):
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
