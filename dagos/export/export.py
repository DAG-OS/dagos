import click
import logging
import re
import shutil
import subprocess


from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup
from pathlib import Path


class ExportError(Exception):
    pass


def get_container_backend():
    container_backends = ["podman", "docker"]
    logging.debug(
        f"Check for a supported container backend: {', '.join(container_backends)}"
    )
    for backend in container_backends:
        if shutil.which(backend):
            logging.info(f"Using {backend} as container backend")
            return backend
    raise ExportError(
        f"""
        No container backend available!
        Please install one of {', '.join(container_backends)} first.
        """
    )


def start_container(backend, image):
    logging.debug("Starting container from provided image")
    subprocess.run(
        f"{backend} run -t {image} sh -c 'ls / > /dev/null'",
        shell=True,
        check=True,
    )
    logging.debug("Grabbing container ID")
    container_id = (
        subprocess.run(
            f"{backend} ps --last 1 | awk -F '[[:space:]]+' '$2 ~ /{image}/ {{ print $1 }}'",
            shell=True,
            check=True,  # Maybe fail ourselves?
            capture_output=True,
        )
        .stdout.decode("utf-8")
        .strip()
    )
    logging.info(f"Started container '{container_id}' from image '{image}'")
    return container_id


def get_image_name(backend, container_id):
    image = (
        subprocess.run(
            f"{backend} ps --all --filter 'id={container_id}' | awk -F '[[:space:]]+' '$1 ~ /{container_id}/ {{ print $2 }}'",
            shell=True,
            check=True,  # Maybe fail ourselves?
            capture_output=True,
        )
        .stdout.decode("utf-8")
        .strip()
    )
    logging.debug(f"Image for container '{container_id}' is '{image}'")
    return image


@click.command(no_args_is_help=True)
@optgroup.group(
    "Container export selection",
    cls=RequiredMutuallyExclusiveOptionGroup,
    help="Provide one of the following for the export.",
)
@optgroup.option("--container-id", help="A container ID.")
@optgroup.option("--image", help="A fully qualified container image.")
@click.option("--output", default="/tmp/dagos-export", help="Output directory on disk.")
def export(image, container_id, output):
    """
    Export a container or container image.
    """
    backend = get_container_backend()

    if container_id:
        image = get_image_name(backend, container_id)
    else:
        container_id = start_container(backend, image)

    logging.info("Creating output directory")
    Path(output).mkdir(parents=True, exist_ok=True)

    image_name = re.sub("(:|/)", "_", image)
    archive = f"{output}/{image_name}.tar"
    logging.debug(f"Exporting '{container_id}' to '{archive}'")
    subprocess.run([backend, "export", "--output", archive, container_id], check=True)

    # TODO:Package additional files together with exported tar file

    if image:
        logging.info(f"Removing started container with ID '{container_id}")
        subprocess.run([backend, "rm", container_id], check=True)

    # TODO: Remove temporary files
