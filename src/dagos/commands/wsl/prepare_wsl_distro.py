import re
import subprocess

import click
from click_option_group import RequiredMutuallyExclusiveOptionGroup, optgroup
from loguru import logger

import dagos.containers.utils as container_utils
from dagos.logging import spinner


class ExportError(Exception):
    pass


@click.command(name="prepare", no_args_is_help=True)
@optgroup.group("Export selection", cls=RequiredMutuallyExclusiveOptionGroup)
@optgroup.option("-c", "--container", help="A container name or ID.")
@optgroup.option("-i", "--image", help="A fully qualified container image.")
@click.option(
    "-o",
    "--output",
    default=".",
    type=click.Path(exists=True),
    help="Output directory on disk.",
)
def prepare_wsl_distro(image, container, output):
    """
    Export the filesystem contents of a container or container image to a tar archive.

    The resulting archive is ready for import as a WSL distro, e.g., via `dagos wsl import`.
    """
    container_engine = container_utils.get_container_engine()

    delete_container = True
    if container:
        delete_container = False
        image = container_utils.get_image_name(container_engine, container)
    else:
        container = container_utils.start_container(
            container_engine, image, "dagos-export"
        )

    image_name = re.sub("[:/]", "_", image)
    archive = f"{output}/{image_name}.tar"
    logger.debug(f"Exporting '{container}' to '{archive}'")
    with spinner("Exporting...", "Successfully exported container"):
        subprocess.run(
            [container_engine, "export", "--output", archive, container],
            check=True,
        )

    # TODO: Package additional files together with exported tar file

    if delete_container:
        logger.debug(f"Removing container '{container}'")
        subprocess.run(
            [container_engine, "rm", container],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        logger.info(f"Removed container '{container}'")

    # TODO: Remove temporary files
