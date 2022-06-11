import subprocess
from contextlib import contextmanager
from unittest.mock import ANY

import pytest
from loguru import logger

from dagos.logging import LogLevel
from dagos.platform import OperatingSystem
from dagos.platform import platform_utils
from dagos.platform import UnsupportedOperatingSystemException
from dagos.platform import UnsupportedPlatformException


@contextmanager
def does_not_raise():
    yield


@pytest.mark.parametrize(
    "system,actual_system,expectation",
    [
        (OperatingSystem.WINDOWS, "Windows", True),
        (OperatingSystem.LINUX, "Windows", False),
    ],
)
def test_is_operating_system(mocker, system, actual_system, expectation):
    mocker.patch("platform.system", return_value=actual_system)
    assert platform_utils.is_operating_system(system) == expectation


@pytest.mark.parametrize(
    "system,expectation",
    [
        ("Windows", does_not_raise()),
        ("Linux", pytest.raises(UnsupportedOperatingSystemException)),
    ],
)
def test_assert_windows(mocker, system, expectation):
    mocker.patch("platform.system", return_value=system)
    with expectation:
        platform_utils.assert_windows()


@pytest.mark.parametrize(
    "system,expectation",
    [
        ("Windows", pytest.raises(UnsupportedOperatingSystemException)),
        ("Linux", does_not_raise()),
    ],
)
def test_assert_linux(mocker, system, expectation):
    mocker.patch("platform.system", return_value=system)
    with expectation:
        platform_utils.assert_linux()


@pytest.mark.parametrize(
    "system,systems,expectation",
    [
        ("Windows", [OperatingSystem.WINDOWS], does_not_raise()),
        ("Linux", [OperatingSystem.LINUX], does_not_raise()),
        ("Linux", [OperatingSystem.WINDOWS, OperatingSystem.LINUX], does_not_raise()),
        ("Linux", [], pytest.raises(UnsupportedOperatingSystemException)),
    ],
)
def test_assert_operating_system(mocker, system, systems, expectation):
    mocker.patch("platform.system", return_value=system)
    with expectation:
        platform_utils.assert_operating_system(systems)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("ls", True),
        ("abcdefqwertz", False),
    ],
)
def test_is_command_available(input, expected):
    assert platform_utils.is_command_available(input) == expected


@pytest.mark.parametrize(
    "input,expectation",
    [
        ("ls", does_not_raise()),
        ("", pytest.raises(UnsupportedPlatformException)),
        ("asdsdhfnhswrwe", pytest.raises(UnsupportedPlatformException)),
    ],
)
def test_assert_command_available(input, expectation):
    with expectation:
        platform_utils.assert_command_available(input)


@pytest.mark.parametrize(
    "system,effective_uid,expectation",
    [
        ("Linux", 0, True),
        ("Linux", 1000, False),
        ("Windows", 1234, False),
    ],
)
def test_is_root(mocker, system, effective_uid, expectation):
    mocker.patch("platform.system", return_value=system)
    mocker.patch("os.geteuid", return_value=effective_uid)
    assert platform_utils.is_root() == expectation


@pytest.mark.parametrize(
    "system,effective_uid,expectation",
    [
        ("Linux", 0, does_not_raise()),
        ("Linux", 1000, pytest.raises(UnsupportedPlatformException)),
        ("Windows", 1234, pytest.raises(UnsupportedPlatformException)),
    ],
)
def test_assert_root_privileges(mocker, system, effective_uid, expectation):
    mocker.patch("platform.system", return_value=system)
    mocker.patch("os.geteuid", return_value=effective_uid)
    with expectation:
        platform_utils.assert_root_privileges()


@pytest.mark.parametrize(
    "command,shell,capture_stdout,capture_stderr,stdout,stderr,encoding,log_level",
    [
        ("command", True, None, None, None, None, None, LogLevel.ERROR),
        (["command"], False, None, None, None, None, None, LogLevel.WARNING),
        (
            ["command"],
            False,
            True,
            None,
            subprocess.PIPE,
            None,
            None,
            LogLevel.INFO,
        ),
        (
            ["command"],
            False,
            False,
            True,
            None,
            subprocess.PIPE,
            None,
            LogLevel.SUCCESS,
        ),
        (["command"], False, True, True, subprocess.PIPE, subprocess.PIPE, None, None),
    ],
)
def test_private_run(
    mocker,
    command,
    shell,
    capture_stdout,
    capture_stderr,
    stdout,
    stderr,
    encoding,
    log_level,
):
    mocker.patch("loguru.logger.log")
    mocker.patch("subprocess.run")

    platform_utils.run_command(
        command,
        capture_stdout,
        capture_stderr,
        ignore_failure=True,
        encoding=encoding,
        log_level=log_level,
    )

    if log_level is not None:
        logger.log.assert_called_once_with(log_level.value, "Running command: {}", ANY)
    subprocess.run.assert_called_once_with(
        command,
        shell=shell,
        stdout=stdout,
        stderr=stderr,
        text=True,
        encoding=encoding,
    )
