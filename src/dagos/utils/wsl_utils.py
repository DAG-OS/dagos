from dataclasses import dataclass
from pathlib import Path

from loguru import logger

from dagos.logging import spinner
from dagos.platform import platform_utils


@dataclass
class WslDistro:
    name: str
    is_default: bool
    is_running: bool
    version: int


def get_installed_distros():
    """Get list of installed distros for further consumption."""
    distro_list = platform_utils.run_command(
        ["wsl", "-l", "-v"], capture_stdout=True, capture_stderr=True, encoding="utf-16"
    ).stdout
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
    run_result = platform_utils.run_command(
        ["wsl", "--unregister", name],
        capture_stdout=True,
        capture_stderr=True,
        ignore_failure=True,
    )
    if run_result.returncode != 0:
        logger.error(f"Failed to unregister '{name}' distro:\n{run_result.stderr}")
        exit(1)


def import_distro(name: str, install_location: Path, archive: Path, version: int):
    logger.info("Starting the WSL import")
    with spinner("Importing..."):
        run_result = platform_utils.run_command(
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
