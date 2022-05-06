import os
import platform
import shutil
import typing as t
from pathlib import Path

from loguru import logger

import dagos.utils.file_utils as file_utils
from .platform_domain import OperatingSystem
from .platform_domain import PlatformScope
from .platform_exceptions import UnsupportedOperatingSystemException
from .platform_exceptions import UnsupportedPlatformException


def is_operating_system(system: OperatingSystem) -> bool:
    return True if platform.system() == system.value else False


def assert_windows() -> None:
    if not is_operating_system(OperatingSystem.WINDOWS):
        raise UnsupportedOperatingSystemException([OperatingSystem.WINDOWS])


def assert_linux() -> None:
    if not is_operating_system(OperatingSystem.LINUX):
        raise UnsupportedOperatingSystemException([OperatingSystem.LINUX])


def assert_operating_system(supported_systems: t.List[OperatingSystem]) -> None:
    if platform.system() not in [x.value for x in supported_systems]:
        raise UnsupportedOperatingSystemException(supported_systems)


def is_command_available(command: str) -> bool:
    return False if shutil.which(command) is None else True


def assert_command_available(command: str) -> None:
    if not is_command_available(command):
        raise UnsupportedPlatformException(
            f"Required command '{command}' is not available!"
        )


def is_root() -> bool:
    if is_operating_system(OperatingSystem.LINUX):
        return os.geteuid() == 0
    # TODO: Implement for other operating systems
    logger.error("Unable to determine if executing user has root privileges")
    return False


def assert_root_privileges() -> None:
    if not is_root():
        raise UnsupportedPlatformException(f"This action requires root privileges!")


def add_binary_to_path(
    binary: Path,
    binary_name: str = None,
    scope: PlatformScope = PlatformScope.USER,
    force: bool = False,
) -> Path:
    """Add provided binary to a directory on the PATH.

    Args:
        binary (Path): The path to the binary.
        binary_name (str, optional): If provided, this changes the name of the linked binary. Defaults to None.
        scope (PlatformScope, optional): The scope to add this binary to. Defaults to PlatformScope.USER.
        force (bool, optional): If existing binaries should be overridden. Defaults to False.

    Raises:
        UnsupportedOperatingSystemException: If a OS other than Linux is used.

    Returns:
        Path: The path of the linked binary
    """
    if not is_operating_system(OperatingSystem.LINUX):
        raise UnsupportedOperatingSystemException(
            "Adding a binary to the PATH is currently only supported on Linux!"
        )

    if binary_name is None:
        binary_name = binary.name
    # TODO: Check if the directory is really included in the PATH?
    dir_on_path = (
        Path("~/.local/bin") if scope == PlatformScope.USER else Path("/usr/local/bin")
    )
    return file_utils.create_symlink(dir_on_path / binary_name, binary, force)
