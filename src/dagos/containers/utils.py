import subprocess

from loguru import logger

from .exceptions import ContainerException
from .exceptions import NoSupportedContainerEngineException
from dagos.logging import spinner
from dagos.platform import platform_utils

selected_container_engine = None


def get_container_engine() -> str:
    global selected_container_engine
    if selected_container_engine != None:
        return selected_container_engine

    supported_container_engines = ["podman", "docker"]
    logger.debug(
        f"Looking for a supported container engine: {', '.join(supported_container_engines)}"
    )
    for engine in supported_container_engines:
        if platform_utils.is_command_available(engine):
            logger.info(f"Using '{engine}' as container engine")
            selected_container_engine = engine
            return engine
    raise NoSupportedContainerEngineException(supported_container_engines)


def start_container(image: str, name="dagos"):
    platform_utils.assert_command_available("awk")
    container_engine = get_container_engine()

    logger.debug("Starting container from provided image")
    with spinner("Starting container..."):
        run_result = subprocess.run(
            f"{container_engine} run -t --name={name} {image} sh -c 'ls / > /dev/null'",
            shell=True,
            stderr=subprocess.PIPE,
        )

    if run_result.returncode != 0:
        stderr = run_result.stderr.decode("utf-8")
        raise ContainerException(
            f"Failed to start container for image '{image}':\n{stderr}"
        )

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


def remove_container(container: str) -> None:
    container_engine = get_container_engine()
    logger.debug(f"Removing container '{container}'")
    subprocess.run(
        [container_engine, "rm", container],
        check=True,
        stdout=subprocess.DEVNULL,
    )
    logger.info(f"Removed container '{container}'")


def container_exists(container: str) -> bool:
    container_engine = get_container_engine()

    result = subprocess.run([container_engine, "container", "exists", container])
    return result.returncode == 0


def get_image_name(container: str) -> str:
    container_engine = get_container_engine()
    if not container_exists(container):
        raise ContainerException(f"No container exists with provided ID '{container}'!")

    image = (
        subprocess.run(
            [
                container_engine,
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
