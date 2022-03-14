import typing as t
from pathlib import Path

import click
from loguru import logger

import dagos.containers.buildah as buildah
from dagos.core.commands import CommandType
from dagos.core.components import SoftwareComponent, SoftwareComponentRegistry
from dagos.core.validator import Validator
from dagos.exceptions import DagosException


@click.command()
@click.option(
    "--container",
    "-c",
    is_flag=True,
    help="""Deploy the environment to a container. Either uses --image option or
            the platform/image option from the environment configuration.""",
)
@click.option(
    "--image",
    "-i",
    required=False,
    help="""The base image to use when --container option is provided. Overrides
            the setting in the provided environment configuration.""",
)
@click.argument(
    "file",
    type=click.Path(file_okay=True, dir_okay=False, readable=True, path_type=Path),
)
def deploy(container: bool, image: str, file: Path):
    """Deploy a provided environment."""
    data = Validator().validate_environment(file.expanduser())
    environment = data["environment"]

    if container:
        image = _get_image(image, environment)
        logger.info(
            "Deploying environment '{}' into '{}' container image",
            environment["name"],
            image,
        )
    else:
        logger.info("Deploying environment '{}'", environment["name"])

    components = _collect_components(environment["components"])
    if container:
        _deploy_to_container(components, image, environment["name"])
    else:
        _deploy_locally(components)


def _get_image(image_option: str, environment: t.Dict) -> str:
    if image_option:
        return image_option
    if "image" in environment["platform"]:
        return environment["platform"]["image"][0]
    raise DagosException(
        f"For deploying an environment to a container a valid base image is required!"
    )


def _collect_components(components: t.List[t.Dict]) -> t.List[SoftwareComponent]:
    collected_components: t.List[SoftwareComponent] = []
    unknown_components: t.List[str] = []
    for component in components:
        found_component = SoftwareComponentRegistry.find_component(component["name"])
        if found_component:
            logger.trace("Requested component '{}' is known!", component["name"])
            # TODO: Check if selected platform supports component?
            collected_components.append(found_component)
        else:
            unknown_components.append(component["name"])

    if len(unknown_components) > 0:
        logger.error(
            "{} of the {} requested components are unknown, specifically: {}",
            len(unknown_components),
            len(components),
            ", ".join(unknown_components),
        )

    return collected_components


def _deploy_locally(components: t.List[SoftwareComponent]) -> None:
    for component in components:
        logger.info("Deploying component '{}'", component.name)
        install_command = component.commands[CommandType.INSTALL.name]
        install_command.execute()


def _deploy_to_container(
    components: t.List[SoftwareComponent], image: str, result_name: str
) -> None:
    container = buildah.create_container(image)

    try:
        # Ensure dagos is installed
        if not buildah.check_command(container, "dagos"):
            # TODO: Check base image meets minimum requirements (dagos or pip,git)
            # TODO: Handle different package managers
            buildah.run(container, "apt update")
            buildah.run(container, "apt install -y python3-pip git")
            buildah.run(
                container,
                "pip3 install git+https://github.com/DAG-OS/dagos.git#egg=dagos",
            )
            # Committing the base image with dagos installed so that users may
            # continue from this image to save time during debugging.
            buildah.commit(container, f"{image}-with-dagos")

        # Copy software components to container
        component_dir = "/root/.dagos/components"
        for component in components:
            buildah.copy(container, component.folders[0], component_dir)

        # Install components
        for component in components:
            buildah.run(container, f"dagos install {component.name}")

        buildah.commit(container, result_name)
    finally:
        buildah.rm(container)
