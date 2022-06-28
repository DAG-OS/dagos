import typing as t
from pathlib import Path

import click
from loguru import logger

import dagos.containers.buildah as buildah
from dagos.core.commands import CommandType
from dagos.core.components import SoftwareComponent
from dagos.core.configuration import DagosConfiguration
from dagos.core.environments import Image
from dagos.core.environments import Packages
from dagos.core.environments import SoftwareEnvironment
from dagos.core.environments import SoftwareEnvironmentBuilder
from dagos.core.package_managers import PackageManager
from dagos.core.package_managers import PackageManagerRegistry
from dagos.exceptions import DagosException
from dagos.platform import CommandRunner
from dagos.platform import ContainerCommandRunner
from dagos.platform.command_runner import LocalCommandRunner


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
    environment = SoftwareEnvironmentBuilder.from_file(file)
    components = environment.collect_components()

    if container:
        chosen_image = _get_image(image, environment)
        logger.info(
            "Deploying environment '{}' into '{}' container image",
            environment.name,
            chosen_image.id,
        )
        _deploy_to_container(environment, components, chosen_image)
    else:
        logger.info("Deploying environment '{}'", environment.name)
        _deploy_locally(environment, components)


def _get_image(image_option: str, environment: SoftwareEnvironment) -> Image:
    if image_option:
        return Image(id=image_option)
    if len(environment.platform.images) > 0:
        # TODO: Allow choosing which image to deploy to?
        return environment.platform.images[0]
    raise DagosException(
        f"For deploying an environment to a container a valid base image is required!"
    )


def _deploy_locally(
    environment: SoftwareEnvironment, components: t.List[SoftwareComponent]
) -> None:
    # TODO: Ensure environment variables are persisted

    def install_component(component: SoftwareComponent):
        logger.info("Deploying component '{}'", component.name)
        install_command = component.commands[CommandType.INSTALL.name]
        install_command.execute()

    _install_packages_and_components(
        LocalCommandRunner(),
        environment.platform.packages,
        components,
        install_component,
    )


def _deploy_to_container(
    environment: SoftwareEnvironment,
    components: t.List[SoftwareComponent],
    image: Image,
) -> None:
    container = buildah.create_container(image.id)
    command_runner = ContainerCommandRunner(container)

    try:
        buildah.config(
            container,
            # TODO: Persist environment variables exactly as in local deployment
            # as the resulting image may be used to import into WSL
            env_vars={x.name: x.value for x in environment.platform.env},
            entrypoint="/bin/bash",
        )

        # Copy software components to container
        component_dir = Path("/opt/dagos/components")
        for component in components:
            buildah.copy(
                container,
                component.folders[0],
                component_dir / component.folders[0].name,
            )

        verbosity = DagosConfiguration().verbosity
        if verbosity == 0:
            verbosity_switch = " "
        elif verbosity == 1:
            verbosity_switch = " -v "
        else:
            verbosity_switch = " -vv "

        def install_component(component: SoftwareComponent):
            if not command_runner.check_command("dagos"):
                _bootstrap_container(container)
            command_runner.run(f"dagos{verbosity_switch}install {component.name}")

        _install_packages_and_components(
            command_runner,
            environment.platform.packages + image.packages,
            components,
            install_component,
        )

        buildah.commit(container, environment.name)
    finally:
        buildah.rm(container)


def _install_packages_and_components(
    command_runner: CommandRunner,
    packages_to_install: t.List[Packages],
    components: t.List[SoftwareComponent],
    # TODO: Add type hint
    install_component,
) -> None:
    # It's important to group packages by manager since there may be several
    # packages defined for a single manager in various places, e.g., general and
    # image related.
    package_bundles: t.Dict[str, Packages] = {}
    for package in packages_to_install:
        if package.manager not in package_bundles:
            package_bundles[package.manager] = None
        if package_bundles[package.manager] is None:
            package_bundles[package.manager] = package
        else:
            package_bundles[package.manager].package_list.extend(package.package_list)

    # TODO: Sort by package manager? For now sorting manually through YAML
    # First system, and named system managers, then anything else
    # What about managers that are installed via components? E.g. SDKMAN?

    for manager, packages in package_bundles.items():
        if manager == "system":
            package_manager = _select_package_manager(command_runner)
        else:
            package_manager = PackageManagerRegistry.find(manager)
            # TODO: Create adhoc manager from name (and options) for unknown managers

        if packages.dependency:
            component = [x for x in components if x.name == packages.dependency]
            if len(component) == 1:
                component = component[0]
                install_component(component)
                components.remove(component)
            elif len(component) == 0:
                raise DagosException(
                    f"""Unable to satisfy dependency '{packages.dependency}'
                    as there is no such component mentioned in this environment."""
                )
            else:
                raise DagosException(
                    f"""Unable to satisfy dependency '{packages.dependency}'
                    as there are too many components with the same name mentioned."""
                )

        if package_manager is None:
            command_runner.run(f"{manager} install {' '.join(packages.package_list)}")
        else:
            package_manager.install(packages.package_list, command_runner)
            package_manager.clean(command_runner)

    # Install remaining components
    for component in components:
        install_component(component)


def _bootstrap_container(container: str) -> None:
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


def _select_package_manager(command_runner: CommandRunner) -> PackageManager:
    for package_manager in PackageManagerRegistry.managers:
        if command_runner.check_command(package_manager.name()):
            return package_manager
    supported_managers = [x.name() for x in PackageManagerRegistry.managers]
    raise DagosException(
        f"None of the supported package managers are available: {', '.join(supported_managers)}"
    )
