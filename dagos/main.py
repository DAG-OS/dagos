import click
import logging
import dagos.commands.import_wsl_distro
import dagos.commands.prepare_wsl_distro

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


main.add_command(dagos.commands.import_wsl_distro.import_wsl_distro)
main.add_command(dagos.commands.prepare_wsl_distro.prepare_wsl_distro)
