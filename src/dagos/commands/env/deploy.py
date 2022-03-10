from pathlib import Path

import click
import yamale
from loguru import logger

from dagos.core.components import SoftwareComponentRegistry


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

    schema_file = Path(__file__).parent.parent.parent / "environments" / "schema.yml"
    schema = yamale.make_schema(schema_file)
    data = yamale.make_data(file)
    try:
        yamale.validate(schema, data)
        logger.debug("Provided environment file '{}' is valid", file)
    except yamale.YamaleError as e:
        logger.error("Provided environment file '{}' is invalid!", file)
        for result in e.results:
            for error in result.errors:
                logger.error(error)

    environment = data[0][0]["environment"]
    logger.info("Deploying environment '{}'", environment["name"])

    # TODO: Check if selected platform is supported

    components = environment["components"]
    for component, values in components.items():
        logger.info("Deploying component '{}'", component)
        if not component in [x.name for x in SoftwareComponentRegistry.components]:
            logger.error("Component '{}' is unknown!", component)
