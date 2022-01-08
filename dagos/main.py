import click
import logging

from dagos.export.export import export


@click.group()
def main():
    logging.basicConfig(level=logging.DEBUG)


main.add_command(export)
