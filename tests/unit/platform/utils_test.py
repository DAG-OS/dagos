from contextlib import contextmanager

import pytest

import dagos.platform.utils as utils
from dagos.platform.domain import OperatingSystem
from dagos.platform.exceptions import UnsupportedOperatingSystem
from dagos.platform.exceptions import UnsupportedPlatformException


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
    assert utils.is_operating_system(system) == expectation


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
    "system,expectation",
    [
        ("Windows", pytest.raises(UnsupportedOperatingSystem)),
        ("Linux", does_not_raise()),
    ],
)
def test_assert_linux(mocker, system, expectation):
    mocker.patch("platform.system", return_value=system)
    with expectation:
        utils.assert_linux()


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
    assert utils.is_root() == expectation


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
        utils.assert_root_privileges()
