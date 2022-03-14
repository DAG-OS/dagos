from pathlib import Path

import pytest

pytest_plugins = [
    "tests.bdd.steps.given_steps",
    "tests.bdd.steps.when_steps",
    "tests.bdd.steps.then_steps",
]


@pytest.fixture
def test_data_dir() -> Path:
    return Path(__file__).parent / "data"
