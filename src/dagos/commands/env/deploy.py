from pathlib import Path

import click
from loguru import logger

from dagos.core.commands import CommandType
from dagos.core.components import SoftwareComponentRegistry
from dagos.core.validator import Validator


@click.command()
@click.argument(
    "file",
    type=click.Path(
        exists=True, file_okay=True, dir_okay=False, readable=True, path_type=Path
    ),
)
def deploy(file: Path):
    """Deploy a provided environment."""
    # TODO: Allow selecting deployment target

    data = Validator().validate_environment(file)
    environment = data["environment"]
    logger.info("Deploying environment '{}'", environment["name"])

    # TODO: Check if selected platform is supported

    # TODO: Validate that all components are known and installable
    components = environment["components"]
    for component in components:
        found_component = SoftwareComponentRegistry.find_component(component["name"])
        if found_component:
            logger.info("Deploying component '{}'", component["name"])
            install_command = found_component.commands[CommandType.INSTALL.name]
            install_command.execute()
        else:
            logger.error("Component '{}' is unknown!", component["name"])
