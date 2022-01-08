import click
import logging

from dagos.export.export import export


@click.group()
def main():
    logging.addLevelName(logging.WARNING, "WARN")
    logging.addLevelName(logging.CRITICAL, "FATAL")
    log_format = "{asctime} [{levelname:<5s}] {message}"
    logging.basicConfig(level=logging.DEBUG, format=log_format, style="{")


main.add_command(export)
