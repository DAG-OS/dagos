from contextlib import contextmanager

import pytest

import dagos.platform.utils as utils
from dagos.platform.domain import OperatingSystem
from dagos.platform.exceptions import (
    UnsupportedOperatingSystem,
    UnsupportedPlatformException,
)


@contextmanager
def does_not_raise():
    yield


@pytest.mark.parametrize(
    "system,expectation",
    [
        ("Windows", True),
        ("Linux", False),
        ("", False),
        (None, False),
    ],
)
def test_is_windows(mocker, system, expectation):
    mocker.patch("platform.system", return_value=system)
    assert utils.is_windows() == expectation


@pytest.mark.parametrize(
    "system,expectation",
    [
        ("Windows", does_not_raise()),
        ("Linux", pytest.raises(UnsupportedOperatingSystem)),
    ],
)
def test_assert_windows(mocker, system, expectation):
    mocker.patch("platform.system", return_value=system)
    with expectation:
        utils.assert_windows()


@pytest.mark.parametrize(
    "system,systems,expectation",
    [
        ("Windows", [OperatingSystem.WINDOWS], does_not_raise()),
        ("Linux", [OperatingSystem.LINUX], does_not_raise()),
        ("Linux", [OperatingSystem.WINDOWS, OperatingSystem.LINUX], does_not_raise()),
        ("Linux", [], pytest.raises(UnsupportedOperatingSystem)),
    ],
)
def test_assert_operating_system(mocker, system, systems, expectation):
    mocker.patch("platform.system", return_value=system)
    with expectation:
        utils.assert_operating_system(systems)


@pytest.mark.parametrize(
    "input,expected",
    [
        ("ls", True),
        ("abcdefqwertz", False),
    ],
)
def test_is_command_available(input, expected):
    assert utils.is_command_available(input) == expected


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
        utils.assert_command_available(input)
