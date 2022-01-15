import ansible_runner
import click
import logging

from pathlib import Path

inventory = "localhost ansible_connection=local"
roles_path = Path.home() / ".ansible" / "roles"


@click.group(name="git", chain=True)
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
    logging.debug("Installing Git")
    ansible_runner.run(
        role="dagos.git",
        roles_path=str(roles_path),
        extravars={"state": "install"},
        inventory=inventory,
    )


@cli.command()
def configure():
    """
    Configure Git.
    """
    logging.debug("Configuring Git")
    ansible_runner.run(
        role="dagos.git",
        roles_path=str(roles_path),
        extravars={"state": "configure"},
        inventory=inventory,
    )
