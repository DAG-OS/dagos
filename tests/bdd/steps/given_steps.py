from pathlib import Path

from pytest_bdd import given, parsers

import dagos.platform.utils as platform_utils
from dagos.commands.wsl.prepare_wsl_distro import start_container


@given("I have root privileges")
def i_have_root_privileges():
    """I have root privileges."""
    platform_utils.assert_root_privileges()


@given(parsers.parse('I have a file "{file}"'), target_fixture="file")
@given(parsers.parse('I have a folder "{file}"'), target_fixture="file")
def i_have_a_file(test_data_dir: Path, file):
    return test_data_dir.joinpath(file)


@given(parsers.parse("I have following text:\n{text}"), target_fixture="text")
def i_have_text(text):
    return text


@given(parsers.parse('I have a running container named "{container_name}"'))
def i_have_container(container_name: str, container_engine):
    start_container(container_engine, "busybox", container_name)
