import sys
import time

import click
import rich_click.rich_click as rich_click
from loguru import logger

from . import __version__
from dagos.commands.env.cli import env
from dagos.commands.list_command import list
from dagos.commands.wsl.cli import wsl
from dagos.core.commands import CommandRegistry
from dagos.core.commands import CommandType
from dagos.core.component_scanner import SoftwareComponentScanner
from dagos.core.configuration import ConfigurationScanner
from dagos.core.environments import SoftwareEnvironmentScanner
from dagos.exceptions import DagosException
from dagos.logging import configure_logging

click.Command.format_help = rich_click.rich_format_help
click.Group.format_help = rich_click.rich_format_help
rich_click.STYLE_HELPTEXT = ""
rich_click.USE_RICH_MARKUP = True
rich_click.COMMAND_GROUPS = {
    "dagos": [
        {
            "name": "General Commands",
            "commands": ["list"],
        },
        {
            "name": "Software Component Commands",
            "commands": [type.value for type in CommandType],
        },
        {"name": "Software Environment Commands", "commands": ["env", "wsl"]},
    ]
}


def timer_callback(ctx: click.Context, param: click.Option, value: bool) -> None:
    if not value or ctx.resilient_parsing:
        return
    start = time.perf_counter()

    def print_elapsed_time():
        stop = time.perf_counter()
        logger.info(f"Elapsed time: {stop-start:0.3f} seconds")

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
    pass


def dagos():
    try:
        use_verbosity_from_configuration = False
        arguments = sys.argv[1:]

        verbosity = 0
        if len(arguments) > 0 and "-v" == arguments[0]:
            verbosity = 1
        elif len(arguments) > 0 and "-vv" == arguments[0]:
            verbosity = 2
        else:
            use_verbosity_from_configuration = True
        configure_logging(verbosity)

        configuration = ConfigurationScanner().scan()
        if use_verbosity_from_configuration:
            configure_logging(configuration.verbosity)
        else:
            configuration.verbosity = verbosity

        SoftwareComponentScanner().scan(configuration.component_search_paths)
        SoftwareEnvironmentScanner().scan(configuration.environment_search_paths)
        for command in CommandRegistry.commands.values():
            dagos_cli.add_command(command)
        dagos_cli.add_command(wsl)
        dagos_cli.add_command(env)
        dagos_cli.add_command(list)
        dagos_cli()
    except DagosException as e:
        logger.error(e)
        exit(1)
    except Exception as e:
        logger.exception(e)
        exit(1)
