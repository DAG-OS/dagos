"""Using custom software components feature tests."""

import subprocess
from pathlib import Path

from pytest_bdd import given, parsers, scenario, then, when


@scenario("custom_components.feature", "Adding a minimal software component")
def test_adding_a_minimal_software_component():
    """Adding a minimal software component."""


@given(parsers.parse("I have following YAML:\n{yaml}"), target_fixture="i_have_yaml")
def i_have_yaml(yaml):
    """I have a YAML based software component"""
    return yaml


@when(parsers.parse('I store this YAML at "{path}"'))
def i_store_this_yaml_in_a_software_component_search_path(i_have_yaml, path):
    """I store this YAML in a software component search path."""
    file = Path(path)
    file.parent.mkdir(parents=True)
    file.write_text(i_have_yaml)


@when(parsers.parse('call "{dagos_command}"'))
def call_dagos_manage_vale_install(dagos_command):
    """call dagos to install component."""
    subprocess.check_call(dagos_command, shell=True)


@then("DAG-OS should install my software component")
def dagos_should_install_my_software_component():
    """DAG-OS should install my software component."""
    subprocess.check_call(["vale", "--version"])
