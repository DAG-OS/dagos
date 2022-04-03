from pathlib import Path

import click
from loguru import logger

import dagos.containers.buildah as buildah
from dagos.core.commands import CommandType
from dagos.core.environments import Image
from dagos.core.environments import SoftwareEnvironment
from dagos.core.package_managers import PackageManager
from dagos.core.package_managers import PackageManagerRegistry
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
    environment = SoftwareEnvironment(file)

    if container:
        chosen_image = _get_image(image, environment)
        logger.info(
            "Deploying environment '{}' into '{}' container image",
            environment.name,
            chosen_image.id,
        )
    else:
        logger.info("Deploying environment '{}'", environment.name)

    if container:
        _deploy_to_container(environment, chosen_image)
    else:
        _deploy_locally(environment)


def _get_image(image_option: str, environment: SoftwareEnvironment) -> Image:
    if image_option:
        return Image(id=image_option)
    if len(environment.platform.images) > 0:
        return environment.platform.images[0]
    raise DagosException(
        f"For deploying an environment to a container a valid base image is required!"
    )


def _deploy_locally(environment: SoftwareEnvironment) -> None:
    for component in environment.collect_components():
        logger.info("Deploying component '{}'", component.name)
        install_command = component.commands[CommandType.INSTALL.name]
        install_command.execute()


def _deploy_to_container(environment: SoftwareEnvironment, image: Image) -> None:
    components = environment.collect_components()
    container = buildah.create_container(image.id)

    try:
        _install_packages(container, image)

        # Ensure dagos is installed
        if not buildah.check_command(container, "dagos"):
            container = _bootstrap_container(container, image)

        # Copy software components to container
        component_dir = Path("/root/.dagos/components")
        for component in components:
            buildah.copy(
                container,
                component.folders[0],
                component_dir / component.folders[0].name,
            )

        # Install components
        for component in components:
            # TODO: Use the same verbosity as the CLI was initially called with
            buildah.run(container, f"dagos install {component.name}")
            # TODO: The components are removed to ensure dagos CLI tests use the correct components
            #   Users may want to keep the copied components on the containers?
            buildah.run(
                container, f"rm -rf {component_dir / component.folders[0].name}"
            )

        buildah.commit(container, environment.name)
    finally:
        buildah.rm(container)


def _install_packages(container: str, image: Image) -> None:
    if len(image.packages) > 0:
        if image.package_manager is not None:
            package_manager = PackageManagerRegistry.find(image.package_manager)
        else:
            # TODO: Analyze platform first and get information from there?
            package_manager = _select_package_manager(container)
        install_command = package_manager.install(image.packages)
        if isinstance(install_command, str):
            buildah.run(container, install_command)
        else:
            for command in install_command:
                buildah.run(container, command)
        clean_command = package_manager.clean()
        if clean_command:
            buildah.run(container, clean_command)


def _bootstrap_container(container: str, image: Image) -> str:
    """Install dagos on the container."""
    # TODO: How important is it to have the exact same version of dagos installed?
    # TODO: Include dagos wheel within dagos to skip git installation and
    #       have the same version calling dagos installed.

    # TODO: Ensure the installed python version is supported
    buildah.run(container, "python3 --version")
    buildah.run(
        container,
        "python3 -m pip install git+https://github.com/DAG-OS/dagos.git#egg=dagos",
    )

    # Committing the base image with dagos installed so that users may
    # continue from this image to save time during debugging.
    intermediate_image = buildah.commit(container, f"{image.id}-with-dagos", rm=True)
    return buildah.create_container(intermediate_image)


def _select_package_manager(container: str) -> PackageManager:
    for package_manager in PackageManagerRegistry.managers:
        if buildah.check_command(container, package_manager.name()):
            return package_manager
    supported_managers = [x.name() for x in PackageManagerRegistry.managers]
    raise DagosException(
        f"None of the supported package managers are available: {', '.join(supported_managers)}"
    )
