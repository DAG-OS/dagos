import shutil
import subprocess
from pathlib import Path

from pytest import fail
from pytest_bdd import parsers
from pytest_bdd import when


@when(parsers.parse('I store this file at "{destination}"'))
@when(parsers.parse('I store this folder at "{destination}"'))
def i_store_file_at_destination(file: Path, destination: str):
    file = file.expanduser()
    destination = Path(destination).expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)
    if file.is_file():
        shutil.copy(file, destination)
    elif file.is_dir():
        shutil.copytree(file, destination)
    else:
        fail("Unhandled file type!")


@when(
    parsers.parse('I store this text at "{destination}"'), target_fixture="destination"
)
def i_store_text_at_destination(text: str, destination: str):
    path = Path(destination).expanduser()
    backup = None
    if path.exists():
        backup = shutil.copy(path, f"{path}.backup")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{text}\n")
    yield path
    if backup == None:
        path.unlink()
    else:
        shutil.copy(backup, path)
        Path(backup).unlink()


@when(parsers.parse('I run "{command}"'), target_fixture="command_output")
@when(parsers.parse('run "{command}"'), target_fixture="command_output")
def run_command(command: str) -> str:
    print(command)
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print(result.stdout)
    assert result.returncode == 0
    return result.stdout
