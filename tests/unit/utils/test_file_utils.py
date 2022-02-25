from contextlib import contextmanager
from pathlib import Path

import pytest

import dagos.utils.file_utils as file_utils
from dagos.exceptions import DagosException


@contextmanager
def does_not_raise():
    yield


@pytest.mark.parametrize(
    "from_path, to_path, force, target_is_dir, expectation",
    [
        ("from", "tox.ini", False, False, does_not_raise()),
        ("from", "tests", False, True, does_not_raise()),
        ("bla", "bla", False, False, pytest.raises(DagosException)),
    ],
)
def test_create_symlink(from_path, to_path, force, target_is_dir, expectation):
    with expectation:
        file_utils.create_symlink(from_path, to_path, force, target_is_dir)
        symlink = Path(from_path)
        exists = symlink.exists()
        is_symlink = symlink.is_symlink()
        Path(from_path).unlink()

        assert exists
        assert is_symlink


@pytest.fixture
def path_fixture():
    path = Path("symlink-test")
    path.touch()
    yield path
    if path.exists():
        path.unlink()


@pytest.mark.parametrize(
    "to_path, force, target_is_dir, expectation",
    [
        ("tox.ini", False, False, pytest.raises(DagosException)),
        ("tox.ini", True, False, does_not_raise()),
        (Path("tox.ini"), True, False, does_not_raise()),
        ("tests", False, True, pytest.raises(DagosException)),
        ("tests", True, True, does_not_raise()),
    ],
)
def test_create_symlink_existing(
    path_fixture, to_path, force, target_is_dir, expectation
):
    with expectation:
        file_utils.create_symlink(path_fixture, to_path, force, target_is_dir)
        assert path_fixture.exists()
        assert path_fixture.is_symlink()
