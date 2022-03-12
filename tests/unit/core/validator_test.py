from contextlib import contextmanager
from pathlib import Path

import pytest

from dagos.core.validator import Validator
from dagos.exceptions import ValidationException


@contextmanager
def does_not_raise():
    yield


@pytest.mark.parametrize(
    "file,expectation",
    [
        ("config/basic.yml", does_not_raise()),
        ("does_not_exist", pytest.raises(ValidationException)),
        ("config/", pytest.raises(ValidationException)),
        ("config/invalid.yml", pytest.raises(ValidationException)),
        ("config/invalid-values.yml", pytest.raises(ValidationException)),
    ],
)
def test_validate_configuration(test_data_dir: Path, file, expectation):
    configuration = test_data_dir.joinpath(file)
    with expectation:
        result = Validator().validate_configuration(configuration)
        assert len(result.keys()) > 0


@pytest.mark.parametrize(
    "file,expectation",
    [
        ("environments/dagos.yml", does_not_raise()),
    ],
)
def test_validate_environment(test_data_dir: Path, file, expectation):
    environment = test_data_dir.joinpath(file)
    with expectation:
        result = Validator().validate_environment(environment)
        assert len(result.keys()) > 0
