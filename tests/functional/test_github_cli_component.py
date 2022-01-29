import shutil
import subprocess
from pathlib import Path

from pytest_bdd import given, parsers, scenario, then, when


@scenario("github_cli_component.feature", "Install the GitHub CLI")
def test_install_the_github_cli():
    """Install the GitHub CLI."""


@scenario(
    "github_cli_component.feature",
    "Installing custom software component via GitHub CLI",
)
def test_installing_custom_component():
    """Installing custom software component via GitHub CLI."""


@given("DAG-OS CLI is installed")
def given_dagos_is_installed():
    """DAG-OS CLI is installed."""


@given("I have root privileges")
def given_i_have_root_privileges():
    """I have root privileges."""


@when(parsers.parse('I call "{dagos_command}"'))
def i_call_dagos_manage_github_install(dagos_command):
    """I call "dagos manage github install"."""
    subprocess.check_call(dagos_command, shell=True)


@given(parsers.parse("I have following YAML:\n{yaml}"), target_fixture="i_have_yaml")
def i_have_yaml(yaml):
    """I have a YAML based software component"""
    print(yaml)
    return yaml


@when(parsers.parse('I store this YAML at "{path}"'), target_fixture="path")
def i_store_this_yaml_in_a_software_component_search_path(i_have_yaml, path):
    """I store this YAML in a software component search path."""
    file = Path(path)
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(i_have_yaml)
    return file


@when(parsers.parse('call "{dagos_command}"'))
def call_dagos_manage_vale_install(dagos_command):
    """call dagos to install component."""
    subprocess.check_call(dagos_command, shell=True)


@then(parsers.parse('"{command}" should be installed'), target_fixture="command")
def dagos_should_install_my_software_component(command):
    """DAG-OS should install my software component."""
    assert shutil.which(command) != None
