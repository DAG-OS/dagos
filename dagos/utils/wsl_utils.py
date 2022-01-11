import logging
import os
import shutil
import subprocess

from dataclasses import dataclass
from dagos.console import console


@dataclass
class WslDistro:
    name: str
    is_default: bool
    is_running: bool
    version: int


def get_installed_distros():
    """Get list of installed distros for further consumption."""
    distro_list = subprocess.run(
        ["wsl", "-l", "-v"], capture_output=True
    ).stdout.decode("utf-16")
    distros = []
    # Skip header line
    for line in distro_list.splitlines()[1:]:
        # Normalize list so its easier to split
        if not line.startswith("*"):
            line = f"- {line.strip()}"
        columns = line.split()
        distro = WslDistro(
            is_default=True if columns[0].startswith("*") else False,
            name=columns[1],
            is_running=True if columns[2] == "Running" else False,
            version=columns[3],
        )
        logging.debug(distro)
        distros.append(distro)
    return distros


def unregister_distro(name):
    run_result = subprocess.run(
        ["wsl", "--unregister", name],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if run_result.returncode != 0:
        logging.error(
            f"Failed to unregister '{name}' distro:\n{run_result.stderr.decode('utf-8')}"
        )
        exit(1)


def import_distro(name, install_location, archive, version):
    logging.info("Starting the WSL import")
    with console.status("Importing...", spinner="material"):
        run_result = subprocess.run(
            [
                "wsl",
                "--import",
                name,
                install_location,
                archive,
                "--version",
                str(version),
            ]
        )
    if run_result.returncode == 0:
        logging.info(f"Successfully imported '{name}' distro")
    else:
        logging.error(f"Failed to import '{name}'")
        exit(1)


def distro_exists(name):
    return any(distro.name == name for distro in get_installed_distros())


def is_on_windows():
    return True if os.name == "nt" else False


def assert_on_windows():
    if not is_on_windows:
        logging.error("This command is only available on Windows!")
        exit(1)


def is_wsl_installed():
    return False if shutil.which("wsl") is None else True


def assert_wsl_is_installed():
    assert_on_windows()
    if not is_wsl_installed():
        logging.error("WSL must be installed but could not be found!")
        exit(1)
