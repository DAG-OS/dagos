import click
import logging

from dagos.export.export import export


@click.group()
@click.option(
    "--verbose", "-v", is_flag=True, default=False, help="Enter verbose mode."
)
def main(verbose):
    logging.addLevelName(logging.WARNING, "WARN")
    logging.addLevelName(logging.CRITICAL, "FATAL")
    log_format = "{asctime} [{levelname:<5s}] {message}"
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format=log_format,
        style="{",
    )


main.add_command(export)
