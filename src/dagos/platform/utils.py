import platform
import shutil
import typing as t

from .domain import OperatingSystem
from .exceptions import UnsupportedOperatingSystem


def is_windows():
    return True if platform.system() == OperatingSystem.WINDOWS.value else False


def assert_windows():
    if not is_windows():
        raise UnsupportedOperatingSystem([OperatingSystem.WINDOWS])


def assert_operating_system(supported_systems: t.List[OperatingSystem]):
    if not platform.system() in [x.value for x in supported_systems]:
        raise UnsupportedOperatingSystem(supported_systems)


def is_command_available(command: str):
    return False if shutil.which(command) is None else True
