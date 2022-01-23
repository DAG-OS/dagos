import logging
import os
import subprocess
import tarfile
from io import StringIO
from pathlib import Path

import click

import dagos.platform.utils as platform_utils
import dagos.utils.file_utils as file_utils
from dagos.console import console
from dagos.platform.domain import OperatingSystem

platform_utils.assert_operating_system([OperatingSystem.LINUX])
# TODO: Think about removing some of these dependencies
platform_utils.assert_command_available("curl")
platform_utils.assert_command_available("grep")
platform_utils.assert_command_available("jq")


@click.group(name="github-cli")
def cli():
    """
    Manage GitHub CLI.

    The GitHub CLI is useful for interacting with GitHub from the command line.
    DAG-OS may use it for downloading software components hosted there.
    Project home: https://github.com/cli/cli
    """
    pass


@cli.command()
@click.pass_context
def install(ctx: click.Context):
    """Install the GitHub CLI.

    Requires sudo privileges and `curl` to be available.
    """
    if not platform_utils.is_root:
        logging.error("This command requires sudo privileges!")
        exit(1)

    logging.debug("Retriving download link for latest release")
    command = StringIO()
    command.write("curl -sL https://api.github.com/repos/cli/cli/releases/latest | ")
    command.write("jq -r '.assets[].browser_download_url' | ")
    command.write("grep linux_amd64 | ")
    command.write("grep .tar.gz")
    result = subprocess.run(command.getvalue(), shell=True, capture_output=True)
    if not result.returncode == 0:
        logging.error("Failed to download latest release!")
        exit(1)

    download_link = result.stdout.strip().decode("utf-8")
    release_archive = file_utils.download_file(download_link)

    def delete_archive():
        logging.trace("Removing donwloaded release")
        release_archive.unlink()

    ctx.call_on_close(delete_archive)

    # TODO: Allow configuring install directory
    # TODO: How to handle installation in root protected folders?
    install_dir = Path("/opt/dagos/managed/github-cli")

    extract_tar_archive(release_archive, install_dir)
    github_cli = install_dir / "bin" / "gh"
    # TODO: Generalize and allow configuration?
    usr_local_bin = Path("/usr/local/bin")
    add_executable_to_path(github_cli, usr_local_bin)


def extract_tar_archive(archive, install_dir):
    logging.debug("Untar downloaded archive")
    with console.status(
        f"Extracting archive to '{install_dir.name}' ...", spinner="material"
    ):
        with tarfile.open(archive) as tar:
            for member in tar.getmembers():
                member.name = member.name.partition("/")[2]
                tar.extract(member, install_dir)


def add_executable_to_path(executable: Path, dir_on_path: Path, exists_ok: bool = True):
    symlink_target = dir_on_path / executable.name
    if symlink_target.exists():
        if exists_ok:
            logging.trace(
                f"Replacing existing '{executable.name}' symlink in '{symlink_target}'"
            )
            symlink_target.unlink()
        else:
            logging.error(
                f"A '{executable.name}' executable is already in '{symlink_target}'..."
            )
            exit(1)
    os.symlink(executable, symlink_target)
