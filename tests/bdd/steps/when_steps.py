import shutil
import subprocess
from pathlib import Path

from pytest import fail
from pytest_bdd import parsers, when


@when(parsers.parse('I store this file at "{destination}"'))
@when(parsers.parse('I store this folder at "{destination}"'))
def i_store_file_at_destination(file: Path, destination: str):
    Path(destination).expanduser().parent.mkdir(parents=True, exist_ok=True)
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
    if path.exists():
        backup = shutil.copy(destination, f"{destination}.backup")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"{text}\n")
    yield path
    if backup:
        shutil.copy(backup, destination)
        Path(backup).unlink()
    else:
        path.unlink()


@when(parsers.parse('I run "{command}"'), target_fixture="command_output")
@when(parsers.parse('run "{command}"'), target_fixture="command_output")
def run_command(command: str) -> str:
    result = subprocess.run(command, shell=True, capture_output=True)
    assert result.returncode == 0
    return result.stdout.decode("utf-8")
