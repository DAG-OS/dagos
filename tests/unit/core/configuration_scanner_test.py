from contextlib import contextmanager
from pathlib import Path

import pytest

from dagos.core.configuration_scanner import ConfigurationScanner
from dagos.exceptions import ValidationException


@contextmanager
def does_not_raise():
    yield


@pytest.mark.parametrize(
    "file,expectation",
    [
        ("config/basic.yml", does_not_raise()),
        ("does_not_exist", pytest.raises(ValidationException)),
        ("config/invalid.yml", pytest.raises(ValidationException)),
    ],
)
def test_load_configuration(test_data_dir: Path, file, expectation):
    config_file = test_data_dir.joinpath(file)
    with expectation:
        result = ConfigurationScanner().load_configuration(config_file)
        assert result.verbosity == 1
