from contextlib import contextmanager

import pytest

import dagos.platform.utils as utils
from dagos.platform.domain import OperatingSystem
from dagos.platform.exceptions import UnsupportedOperatingSystem


@contextmanager
def does_not_raise():
    yield


def test_is_windows(mocker):
    mocker.patch("platform.system", return_value="Windows")
    assert utils.is_windows() == True


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
    [("ls", True), ("abcdefqwertz", False)],
)
def test_is_command_available(input, expected):
    assert utils.is_command_available(input) == expected
