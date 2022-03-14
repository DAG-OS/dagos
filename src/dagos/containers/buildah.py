import subprocess
import typing as t
from pathlib import Path

from loguru import logger


def _run(
    command: t.Union[str, t.List[str]],
    capture_stdout=False,
    capture_stderr=False,
    ignore_failure=False,
) -> subprocess.CompletedProcess:
    logger.info(
        f"Running command: {command if isinstance(command, str) else ' '.join(command)}"
    )

    result = subprocess.run(
        command,
        shell=True if isinstance(command, str) else False,
        stdout=subprocess.PIPE if capture_stdout else None,
        stderr=subprocess.PIPE if capture_stderr else None,
        text=True,
    )

    # TODO: Exception handling
    if not ignore_failure:
        result.check_returncode()
    return result


def _unwind_dict(arg: str, dict: t.Dict[str, str]) -> t.List[str]:
    result = []
    for key, value in dict.items():
        result.extend([arg, f"{key}={value}"])
    return result


def _unwind_list(arg: str, items: t.List[str]) -> t.List[str]:
    result = []
    for item in items:
        result.extend([arg, item])
    return result


def create_container(
    container_image: str,
    name: str = None,
    volumes: t.List[str] = None,
) -> str:
    """Create a new working container from provided container image.

    Args:
        container_image (str): The container image to start from.
        name (str, optional): The container name.
        volumes (t.List[str], optional): Any volumes to bind into the container.

    Returns:
        str: The container name/id used for further manipulation.
    """
    args = []
    if name:
        args.extend(["--name", name])
    if volumes:
        args.extend(_unwind_list("--volume", volumes))

    command = ["buildah", "from"] + args + [container_image]
    result = _run(command, capture_stdout=True)
    container = result.stdout.strip()
    logger.success(f"Created '{container}' from image '{container_image}'")
    return container


def commit(
    container: str,
    image_name: t.Optional[str] = None,
    rm: bool = False,
    squash: bool = False,
) -> str:
    """Write a new image using the container's read-write layer and, if it is
    based on an image, the layers of that image.

    Args:
        container (str): The container to commit.
        image_name (str, optional): The name of the resulting image.
        rm (bool, optional): If True, remove the container after committing it to an image. Defaults to False.
        squash (bool, optional): If True, squash all images layers into one. Defaults to False.

    Returns:
        str: The committed image ID.
    """
    command = ["buildah", "commit"]

    if rm:
        command.append("--rm")
    if squash:
        command.append("--squash")
    command.append(container)
    if image_name:
        command.append(image_name)

    result = _run(command, capture_stdout=True)
    image = result.stdout.strip()
    logger.info(f"Committed image '{image_name if image_name else image}'")
    return image


def config(
    container: str,
    annotations: t.Optional[t.Dict[str, str]] = None,
    author: t.Optional[str] = None,
    cmd: t.Optional[str] = None,
    created_by: t.Optional[str] = None,
    entrypoint: t.Optional[str] = None,
    env_vars: t.Optional[t.Dict[str, str]] = None,
    labels: t.Optional[t.Dict[str, str]] = None,
    ports: t.Optional[t.List[str]] = None,
    shell: t.Optional[str] = None,
    user: t.Optional[str] = None,
    volumes: t.Optional[t.List[str]] = None,
    working_dir: t.Optional[str] = None,
) -> None:
    """Modify container configuration values saved to the image.

    Args:
        container (str): The container to configure.
        annotations (t.Dict[str, str], optional): Image annotations.
        author (str, optional): Image author contact information.
        cmd (str, optional): The default command to run for containers based on the image.
        created_by (str, optional): A description of how the image was created.
        entrypoint (str, optional): The entrypoint for containers based on the image.
        env_vars (t.Dict[str, str], optional): Environment variables to be set when running containers based on the image.
        labels (t.Dict[str, str], optional): Image labels.
        ports (t.List[str], optional): Ports to expose when running containers based on the image.
        shell (str, optional): Shell to run in containers.
        user (str, optional): Default user to run inside containers based on the image.
        volumes (t.List[str], optional): Default volume paths to be created for containers based on the image.
        working_dir (str, optional): The working directory for containers based on the image.
    """
    args = []
    if annotations:
        args.extend(_unwind_dict("--annotation", annotations))
    if author:
        args.extend(["--author", author])
    if cmd:
        args.extend(["--cmd", cmd])
    if created_by:
        args.extend(["--created-by", created_by])
    if entrypoint:
        args.extend(["--entrypoint", entrypoint])
    if env_vars:
        args.extend(_unwind_dict("--env", env_vars))
    if labels:
        args.extend(_unwind_dict("--label", labels))
    if ports:
        args.extend(_unwind_list("--port", ports))
    if shell:
        args.extend(["--shell", shell])
    if user:
        args.extend(["--user", user])
    if volumes:
        args.extend(_unwind_list("--volume", volumes))
    if working_dir:
        args.extend(["--workingdir", working_dir])

    if args:
        command = ["buildah", "config"] + args + [container]
        _run(command)


def copy(
    container: str,
    src: t.Union[str, Path],
    dst: t.Optional[t.Union[str, Path]] = None,
    chown: t.Optional[str] = None,
) -> None:
    """Copy the contents of a file, URL, or directory into a container's working
    directory.

    Args:
        container (str): The container to copy the contents to.
        src (str | Path): The content source.
        dst (str | Path, optional): The destination in the container.
        chown (str, optional): The user[:group] ownership of the destination content.
    """
    path_to_str = lambda x: x if isinstance(x, str) else x.as_posix()

    command = ["buildah", "copy"]
    if chown:
        command.extend(["--chown", chown])
    command.extend([container, path_to_str(src)])
    if dst:
        command.append(path_to_str(dst))
    _run(command)


def rm(container: str) -> None:
    """Remove provided container.

    Args:
        container (str): The container to remove.
    """
    _run(["buildah", "rm", container])


def run(
    container: str,
    command: t.Union[str, t.List[str]],
    user: t.Optional[str] = None,
    capture_stdout: t.Optional[bool] = False,
    capture_stderr: t.Optional[bool] = False,
    ignore_failure: t.Optional[bool] = False,
) -> subprocess.CompletedProcess:
    """Run provided command using the container's root filesystem, using config
    settings inherited from the container's image or as specified during previous
    calls to the config command.

    Args:
        container (str): The container to run the command in.
        command (t.Union[str, t.List[str]]): The command to run.
        user (str, optional): The user[:group] to run the command as.
        capture_stdout (bool, optional): If True, capture stdout for later retrieval. Defaults to False.
        capture_stderr (bool, optional): If True, capture stderr for later retrieval. Defaults to False.
        ignore_failure (bool, optional): If True, do not fail if the command fails. Defaults to False.

    Returns:
        subprocess.CompletedProcess: The result of running the command.
    """
    run_command = ["buildah", "run"]
    if user:
        run_command.extend(["--user", user])
    run_command.extend([container, "--"])
    run_command.extend(command.split() if isinstance(command, str) else command)
    return _run(run_command, capture_stdout, capture_stderr, ignore_failure)


def check_command(container: str, command: str, user: t.Optional[str] = None) -> bool:
    """Check if provided command is available in provided container.

    Args:
        container (str): The container to check in.
        command (str): The command to check availability for.
        user (t.Optional[str], optional): The user[:group] to check for. Defaults to None.

    Returns:
        bool: True, if the command is available, false otherwise.
    """
    result = run(
        container,
        f"command -v {command}",
        user=user,
        capture_stdout=True,
        capture_stderr=True,
        ignore_failure=True,
    )
    return result.returncode == 0
