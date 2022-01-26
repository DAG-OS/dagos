import logging
import time

import click

from dagos.commands.manage.cli import manage
from dagos.commands.wsl.cli import wsl
from dagos.exceptions import DagosException
from dagos.logging import configure_logging

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
    "--verbose",
    "-v",
    count=True,
    help="Enter verbose mode. Increase verbosity with -vv.",
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
def dagos_cli(verbose: int, timer: bool):
    configure_logging(verbose)


def dagos():
    try:
        dagos_cli()
    except DagosException as e:
        logging.error(e)
        exit(1)
    except Exception as e:
        logging.exception(e)
        exit(1)


dagos_cli.add_command(manage)
dagos_cli.add_command(wsl)
