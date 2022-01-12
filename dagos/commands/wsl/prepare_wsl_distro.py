import click
import logging
import re
import shutil
import subprocess


from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup
from dagos.console import console


class ExportError(Exception):
    pass


@click.command(name="prepare", no_args_is_help=True)
@optgroup.group("Export selection", cls=RequiredMutuallyExclusiveOptionGroup)
@optgroup.option("--container-id", help="A container ID.")
@optgroup.option("--image", help="A fully qualified container image.")
@click.option(
    "-o",
    "--output",
    default=".",
    type=click.Path(exists=True),
    help="Output directory on disk.",
)
def prepare_wsl_distro(image, container_id, output):
    """
    Export a container or container image.
    """
    container_engine = get_container_engine()

    delete_container = True
    if container_id:
        delete_container = False
        image = get_image_name(container_engine, container_id)
    else:
        container_id = start_container(container_engine, image)

    image_name = re.sub("(:|/)", "_", image)
    archive = f"{output}/{image_name}.tar"
    logging.debug(f"Exporting '{container_id}' to '{archive}'")
    with console.status("Exporting...", spinner="material"):
        subprocess.run(
            [container_engine, "export", "--output", archive, container_id],
            check=True,
        )
    logging.info("Successfully exported container")

    # TODO: Package additional files together with exported tar file

    if delete_container:
        logging.debug(f"Removing container '{container_id}'")
        subprocess.run(
            [container_engine, "rm", container_id],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        logging.info(f"Removed container '{container_id}'")

    # TODO: Remove temporary files


def get_container_engine():
    supported_container_engines = ["podman", "docker"]
    logging.debug(
        f"Looking for a supported container engine: {', '.join(supported_container_engines)}"
    )
    for container_engine in supported_container_engines:
        if shutil.which(container_engine):
            logging.info(f"Using '{container_engine}' as container engine")
            return container_engine
    logging.error(
        f"Please install a supported container engine ({', '.join(supported_container_engines)})"
    )
    exit(1)


def start_container(container_engine, image):
    logging.debug("Starting container from provided image")
    with console.status("Starting container...", spinner="material"):
        run_result = subprocess.run(
            f"{container_engine} run -t {image} sh -c 'ls / > /dev/null'",
            shell=True,
            stderr=subprocess.PIPE,
        )
    if run_result.returncode != 0:
        logging.error(
            f"Failed to start container for image '{image}':\n{run_result.stderr.decode('utf-8')}"
        )
        exit(1)

    logging.debug("Grabbing container ID")
    container_id = (
        subprocess.run(
            f"{container_engine} ps --last 1 | awk -F '[[:space:]]+' '$2 ~ /{image}/ {{ print $1 }}'",
            shell=True,
            check=True,
            capture_output=True,
        )
        .stdout.decode("utf-8")
        .strip()
    )
    logging.info(f"Started container '{container_id}' from image '{image}'")
    return container_id


def get_image_name(container_engine, container_id):
    container_exists = subprocess.run(
        [container_engine, "container", "exists", container_id]
    )
    if container_exists.returncode != 0:
        logging.error(f"No container exists with provided ID '{container_id}'!")
        exit(1)
    image = (
        subprocess.run(
            f"{container_engine} ps --all --filter 'id={container_id}' | awk -F '[[:space:]]+' '$1 ~ /{container_id}/ {{ print $2 }}'",
            shell=True,
            check=True,
            capture_output=True,
        )
        .stdout.decode("utf-8")
        .strip()
    )

    try:
        if len(image) == 0:
            raise ExportError(
                f"Failed to get image name for container '{container_id}'!"
            )
    except ExportError:
        console.print_exception()
        exit(1)

    logging.debug(f"Image for container '{container_id}' is '{image}'")
    return image
