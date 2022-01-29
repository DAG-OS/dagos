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
