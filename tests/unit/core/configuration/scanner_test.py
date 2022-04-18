from contextlib import contextmanager
from pathlib import Path

import pytest

from dagos.core.configuration import ConfigurationScanner
from dagos.core.configuration.configuration_domain import DefaultPlaceholder
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
        instance = ConfigurationScanner()
        instance.load_configuration(config_file)

        assert instance.configuration.verbosity == 1
        assert not isinstance(instance.configuration.verbosity, DefaultPlaceholder)


def test_load_multiple_configurations(test_data_dir: Path):
    instance = ConfigurationScanner()
    instance.load_configuration(test_data_dir.joinpath("config/basic.yml"))
    instance.load_configuration(test_data_dir.joinpath("config/another.yml"))

    assert instance.configuration.verbosity == 1
    assert len(instance.configuration.search_paths) == 1
    assert not isinstance(instance.configuration._search_paths, DefaultPlaceholder)
    assert not isinstance(instance.configuration._verbosity, DefaultPlaceholder)
    assert not isinstance(
        instance.configuration._component_search_paths, DefaultPlaceholder
    )
    assert not isinstance(
        instance.configuration._environment_search_paths, DefaultPlaceholder
    )
