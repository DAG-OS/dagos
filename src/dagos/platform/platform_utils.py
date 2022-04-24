import os
import platform
import shutil
import typing as t

from loguru import logger

from .platform_domain import OperatingSystem
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
