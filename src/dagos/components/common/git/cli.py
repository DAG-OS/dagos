import logging
from pathlib import Path

import ansible_runner
import click
import yaml

from dagos.components.domain import SoftwareComponent

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
    logging.info("Installing Git")
    ansible_runner.run(
        role="dagos.git",
        roles_path=str(roles_path),
        extravars={"state": "install"},
        inventory=inventory,
    )


@cli.command()
@click.pass_context
def configure(ctx: click.Context):
    """
    Configure Git.
    """
    logging.info("Configuring Git")

    component: SoftwareComponent = ctx.obj
    if component.config.exists():
        with open(component.config) as f:
            config_values = yaml.safe_load(f)
        if config_values["git_settings"]:
            git_settings = config_values["git_settings"]
    extravars = {
        "state": "configure",
        "git_settings": git_settings,
    }

    ansible_runner.run(
        role="dagos.git",
        roles_path=str(roles_path),
        extravars=extravars,
        inventory=inventory,
    )
