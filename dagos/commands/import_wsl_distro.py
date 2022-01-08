import click
import shutil
import subprocess
import logging


@click.command(name="import")
def import_wsl_distro():
    if shutil.which("wsl") is None:
        logging.critical("wsl must be installed!")
        exit(1)
    # Ensure WSL2 is installed?

    # Get distro name
    # - Let user provide one
    # - Use folder name
    # Store chosen name in a meta file for unregistering the distro later on

    # Ensure the distro name is unique
    subprocess.run(["wsl", "-l", "-v"])

    # Import the distro
    # wsl --import <DistroName> <InstallLocation> <InstallTarFile> --version 2

    # Export DISPLAY?

    # Allow running user scripts?

    # Ask to set default?

    # Print usage information
