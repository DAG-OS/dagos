import subprocess

from loguru import logger

import dagos.platform.utils as platform_utils
from dagos.logging import spinner
from dagos.platform.exceptions import UnsupportedPlatformException


def get_container_engine() -> str:
    supported_container_engines = ["podman", "docker"]
    logger.debug(
        f"Looking for a supported container engine: {', '.join(supported_container_engines)}"
    )
    for container_engine in supported_container_engines:
        if platform_utils.is_command_available(container_engine):
            logger.info(f"Using '{container_engine}' as container engine")
            return container_engine
    raise UnsupportedPlatformException(
        f"No supported container engine found! Please install one of {', '.join(supported_container_engines)}"
    )


def start_container(container_engine, image, name="dagos"):
    logger.debug("Starting container from provided image")
    with spinner("Starting container..."):
        run_result = subprocess.run(
            f"{container_engine} run -t --name={name} {image} sh -c 'ls / > /dev/null'",
            shell=True,
            stderr=subprocess.PIPE,
        )
    if run_result.returncode != 0:
        logger.error(
            f"Failed to start container for image '{image}':\n{run_result.stderr.decode('utf-8')}"
        )
        exit(1)

    logger.debug("Grabbing container ID")
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
    logger.info(f"Started container '{container_id}' from image '{image}'")
    return container_id


def get_image_name(container_engine, container):
    container_exists = subprocess.run(
        [container_engine, "container", "exists", container]
    )
    if container_exists.returncode != 0:
        logger.error(f"No container exists with provided ID '{container}'!")
        exit(1)

    image = (
        subprocess.run(
            [
                "podman",
                "container",
                "inspect",
                container,
                "--format",
                r"{{.ImageName}}",
            ],
            check=True,
            capture_output=True,
        )
        .stdout.decode("utf-8")
        .strip()
    )

    logger.debug(f"Image for container '{container}' is '{image}'")
    return image
