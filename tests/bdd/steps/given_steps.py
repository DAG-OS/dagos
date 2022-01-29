from pathlib import Path

from pytest_bdd import given, parsers


@given("I have root privileges")
def i_have_root_privileges():
    """I have root privileges."""


@given(parsers.parse('I have a file "{file}"'), target_fixture="file")
def i_have_a_file(test_data_dir: Path, file):
    return test_data_dir.joinpath(file)
