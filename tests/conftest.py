from pathlib import Path

import pytest
from _pytest.python import Function

pytest_plugins = [
    "tests.bdd.steps.given_steps",
    "tests.bdd.steps.when_steps",
    "tests.bdd.steps.then_steps",
]


@pytest.fixture
def test_data_dir() -> Path:
    return Path(__file__).parent / "data"


def by_fspath(item: Function):
    return item.fspath


def pytest_collection_modifyitems(items):
    """Sorts tests by their path, which results in BDD tests are run after unit
    tests.
    """
    items.sort(key=by_fspath, reverse=True)
