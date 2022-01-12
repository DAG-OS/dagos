import click
import logging
import os

from dagos.utils import wsl_utils
from pathlib import Path


@click.command(name="import")
@click.option(
    "--name",
    required=True,
    help="Distro name to register.",
)
@click.option(
    "--archive",
    required=True,
    help="Archive path to import, both .tar and .tar.gz are supported.",
)
@click.option(
    "--force",
    "-f",
    is_flag=True,
    default=False,
    help="""
        Force import even if a distro with the same name exists.
        Warning: This will unregister the existing distro.
    """,
)
def import_wsl_distro(name, archive, force):
    """
    Import a WSL distro from a .tar or .tar.gz file.
    """
    wsl_utils.assert_wsl_is_installed()
    check_if_distro_exists(name, force)
    check_archive_validity(archive)

    # Create a folder at install location with the name of the distro and install there
    # TODO: Ensure name can be a folder name
    install_location = f"{os.getcwd()}\{name}"
    Path(install_location).mkdir(exist_ok=True)

    wsl_utils.import_distro(name, install_location, archive, 2)

    # Check if distro has a user configured in /etc/wsl.conf?
    # If not, ask for a user name and configure it

    # Export DISPLAY? Only on < Windows 11?

    # Allow running user scripts?

    # Ask to set default?

    # Print usage information


def check_if_distro_exists(name, force):
    if wsl_utils.distro_exists(name):
        if force:
            logging.warning(f"Unregistering existing '{name}' distro")
            wsl_utils.unregister_distro(name)
        else:
            logging.error(
                f"There already exists a '{name}' distro! Use --force to continue."
            )
            exit(1)


def check_archive_validity(archive):
    archive_path = Path(archive)
    if archive_path.exists():
        logging.debug("Provided archive exists")
    else:
        logging.error(f"No archive exists at '{archive}'")
        exit(1)
    accepted_suffixes = [".tar", ".tar.gz"]
    if archive_path.suffix in accepted_suffixes:
        logging.debug("Provided archive has correct file extension")
    else:
        logging.error(
            f"Provided archive must be one of {''.join(accepted_suffixes)}, but is '{archive_path.suffix}'"
        )
        exit(1)
