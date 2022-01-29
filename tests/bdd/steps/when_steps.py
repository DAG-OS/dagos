import shutil
import subprocess
from pathlib import Path

from pytest_bdd import parsers, when


@when(parsers.parse('I store this file at "{path}"'))
def i_store_file_at_path(file: Path, path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(file, path)


@when(parsers.parse('I run "{command}"'))
@when(parsers.parse('run "{command}"'))
def run_command(command):
    subprocess.check_call(command, shell=True)
