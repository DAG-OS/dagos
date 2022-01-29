import subprocess
from pathlib import Path

from pytest_bdd import parsers, when


@when(parsers.parse('I call "{dagos_command}"'))
def i_call_dagos_manage_github_install(dagos_command):
    """I call "dagos manage github install"."""
    subprocess.check_call(dagos_command, shell=True)


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
