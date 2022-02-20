from pathlib import Path

import pytest

import dagos.containers.utils as container_utils

pytest_plugins = [
    "tests.bdd.steps.given_steps",
    "tests.bdd.steps.when_steps",
    "tests.bdd.steps.then_steps",
]


@pytest.fixture
def test_data_dir() -> Path:
    return Path(__file__).parent / "data"


@pytest.fixture
def container_engine() -> str:
    return container_utils.get_container_engine()
