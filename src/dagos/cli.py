import logging
import time
from pathlib import Path

import click
import rich_click

from dagos.commands.wsl.cli import wsl
from dagos.core.commands import CommandRegistry, CommandType
from dagos.core.component_scanner import SoftwareComponentScanner
from dagos.exceptions import DagosException
from dagos.logging import configure_logging

from . import __version__

click.Command.format_help = rich_click.rich_format_help
click.Group.format_help = rich_click.rich_format_help

rich_click.core.COMMAND_GROUPS = {
    "dagos": [
        {
            "name": "Software Component Commands",
            "commands": [type.value for type in CommandType],
        },
    ]
}
rich_click.core.COMMANDS_PANEL_TITLE = "General Commands"


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
@click.pass_context
def dagos_cli(ctx: click.Context, verbose: int, timer: bool):
    """"""


# TODO: Make this list configurable
component_search_paths = [
    # user
    Path.home() / ".dagos" / "components",
    # system (linux)
    Path("/opt/dagos/components"),
    # dagos
    Path(__file__).parent / "components",
]


def dagos():
    try:
        configure_logging(2)
        SoftwareComponentScanner().scan(component_search_paths)
        for command_group in CommandRegistry.commands.values():
            dagos_cli.add_command(command_group)
        dagos_cli.add_command(wsl)
        dagos_cli()
    except DagosException as e:
        logging.error(e)
        exit(1)
    except Exception as e:
        logging.exception(e)
        exit(1)
