from pathlib import Path

import pytest

from dagos.commands.wsl.prepare_wsl_distro import get_container_engine

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
    return get_container_engine()
