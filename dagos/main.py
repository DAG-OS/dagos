import click
import logging

from dagos.commands.wsl.group import wsl

from rich.logging import RichHandler


@click.group()
@click.option(
    "--verbose", "-v", is_flag=True, default=False, help="Enter verbose mode."
)
def main(verbose):
    log_format = "{message}"
    date_format = "%Y-%m-%d %H:%M:%S"
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format=log_format,
        datefmt=date_format,
        style="{",
        handlers=[RichHandler(rich_tracebacks=True)],
    )


main.add_command(wsl)
