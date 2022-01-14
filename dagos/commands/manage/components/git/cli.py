import click
import logging


@click.group(name="git")
def cli():
    """
    Install or configure Git on your machine.
    """
    pass


@cli.command()
def install():
    """
    Install Git.
    """
    logging.info("Installing Git")


@cli.command()
def configure():
    """
    Configure Git.
    """
    logging.info("Configuring Git")
