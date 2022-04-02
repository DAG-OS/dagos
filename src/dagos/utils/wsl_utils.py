import subprocess
from dataclasses import dataclass
from pathlib import Path

from loguru import logger

import dagos.platform.utils as platform_utils
from dagos.logging import spinner


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
        logger.trace(distro)
        distros.append(distro)
    return distros


def unregister_distro(name):
    run_result = subprocess.run(
        ["wsl", "--unregister", name],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if run_result.returncode != 0:
        logger.error(
            f"Failed to unregister '{name}' distro:\n{run_result.stderr.decode('utf-8')}"
        )
        exit(1)


def import_distro(name: str, install_location: Path, archive: Path, version: int):
    logger.info("Starting the WSL import")
    with spinner("Importing..."):
        run_result = subprocess.run(
            [
                "wsl",
                "--import",
                name,
                str(install_location),
                str(archive),
                "--version",
                str(version),
            ]
        )
    if run_result.returncode == 0:
        logger.info(f"Successfully imported '{name}' distro")
    else:
        logger.error(f"Failed to import '{name}'")
        exit(1)


def distro_exists(name):
    return any(distro.name == name for distro in get_installed_distros())


def assert_wsl_is_installed():
    platform_utils.assert_windows()
    if not platform_utils.is_command_available("wsl"):
        logger.error("WSL must be installed but could not be found!")
        exit(1)
