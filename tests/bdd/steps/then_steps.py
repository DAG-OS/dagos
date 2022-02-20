import re
import shutil
import subprocess
from pathlib import Path

from pytest_bdd import parsers, then


@then(parsers.parse('"{command}" is installed'))
def command_shoud_be_installed(command):
    assert shutil.which(command) != None


@then(parsers.parse('"{file}" is created'))
def file_is_created(file):
    assert Path(file).exists()


@then(parsers.parse('I delete "{file}"'))
def delete_file(file):
    Path(file).unlink()


@then(parsers.parse('I stop the "{container_name}" container'))
def stop_container(container_name, container_engine):
    subprocess.check_call(f"{container_engine} stop {container_name}", shell=True)


@then(parsers.parse('remove the "{container_name}" container'))
def stop_container(container_name, container_engine):
    subprocess.check_call(f"{container_engine} rm {container_name}", shell=True)


@then(parsers.parse('I see "{expected_output}"'))
def i_see(expected_output, command_output: str):
    assert expected_output in command_output


@then(parsers.parse('I see a command "{command}" with the description "{description}"'))
def i_see_command_with_description(command, description, command_output: str):
    pattern = f"{command} +{description}"
    assert re.search(pattern, command_output)


@then(parsers.parse('''I don't see a command "{command}"'''))
def i_dont_see_command(command, command_output: str):
    pattern = f"{command} +\w"
    assert not re.search(pattern, command_output)


@then(parsers.parse('I see "{pattern}" messages'))
def i_see_messages(pattern, command_output: str):
    result = re.search(pattern, command_output)
    assert result


@then(parsers.parse('I see no "{pattern}" messages'))
def i_see_no_messages(pattern, command_output: str):
    result = re.search(pattern, command_output)
    assert not result
