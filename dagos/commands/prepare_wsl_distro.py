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
        f"Checking for a supported container backend: {', '.join(container_backends)}"
    )
    for backend in container_backends:
        if shutil.which(backend):
            logging.info(f"Detected {backend} as container backend")
            return backend
    logging.critical(
        f"Please install a supported container backend ({', '.join(container_backends)})"
    )
    exit(1)


def start_container(backend, image):
    logging.debug("Starting container from provided image")
    run_result = subprocess.run(
        f"{backend} run -t {image} sh -c 'ls / > /dev/null'",
        shell=True,
        stderr=subprocess.PIPE,
    )
    if run_result.returncode != 0:
        logging.critical(
            f"Failed to start container for image '{image}':\n{run_result.stderr.decode('utf-8')}"
        )
        exit(1)

    logging.debug("Grabbing container ID")
    container_id = (
        subprocess.run(
            f"{backend} ps --last 1 | awk -F '[[:space:]]+' '$2 ~ /{image}/ {{ print $1 }}'",
            shell=True,
            check=True,
            capture_output=True,
        )
        .stdout.decode("utf-8")
        .strip()
    )
    logging.info(f"Started container '{container_id}' from image '{image}'")
    return container_id


def get_image_name(backend, container_id):
    container_exists = subprocess.run([backend, "container", "exists", container_id])
    if container_exists.returncode != 0:
        logging.critical(f"No container exists with provided ID '{container_id}'!")
        exit(1)
    image = (
        subprocess.run(
            f"{backend} ps --all --filter 'id={container_id}' | awk -F '[[:space:]]+' '$1 ~ /{container_id}/ {{ print $2 }}'",
            shell=True,
            check=True,
            capture_output=True,
        )
        .stdout.decode("utf-8")
        .strip()
    )
    if len(image) == 0:
        raise ExportError(f"Failed to get image name for container '{container_id}'!")
    logging.debug(f"Image for container '{container_id}' is '{image}'")
    return image


@click.command(name="prepare", no_args_is_help=True)
@optgroup.group("Export selection", cls=RequiredMutuallyExclusiveOptionGroup)
@optgroup.option("--container-id", help="A container ID.")
@optgroup.option("--image", help="A fully qualified container image.")
@click.option("--output", default="/tmp/dagos-export", help="Output directory on disk.")
def prepare_wsl_distro(image, container_id, output):
    """
    Export a container or container image.
    """
    backend = get_container_backend()

    if container_id:
        image = get_image_name(backend, container_id)
    else:
        container_id = start_container(backend, image)

    logging.debug("Creating output directory")
    Path(output).mkdir(parents=True, exist_ok=True)
    logging.info("Created output directory")

    image_name = re.sub("(:|/)", "_", image)
    archive = f"{output}/{image_name}.tar"
    logging.debug(f"Exporting '{container_id}' to '{archive}'")
    subprocess.run([backend, "export", "--output", archive, container_id], check=True)

    # TODO: Package additional files together with exported tar file

    if image:
        logging.debug(f"Removing container '{container_id}'")
        subprocess.run(
            [backend, "rm", container_id], check=True, stdout=subprocess.DEVNULL
        )
        logging.info(f"Removed container '{container_id}'")

    # TODO: Remove temporary files
