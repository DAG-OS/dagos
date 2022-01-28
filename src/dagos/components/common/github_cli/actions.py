import atexit
import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

import click
import yaml

from dagos.components.domain import Action
from dagos.components.exceptions import SoftwareComponentScanException
from dagos.utils import file_utils


class GitHubCliInstallAction(Action):
    """Install a software component from GitHub using the GitHub CLI."""

    name: str
    repository: str
    pattern: str
    install_dir: str

    @staticmethod
    def parse_action(path: Path):
        if not path.exists():
            raise SoftwareComponentScanException("Action file does not exist")
        try:
            with path.open() as f:
                yaml_content = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise SoftwareComponentScanException("YAML is invalid", e)

        action = GitHubCliInstallAction()
        # TODO: Handle optional values
        # TODO: Add error handling
        action.name = yaml_content["name"]
        action.repository = yaml_content["repository"]
        action.pattern = yaml_content["pattern"]
        action.install_dir = yaml_content["install_dir"]
        # TODO: Strip root component?
        return action

    def execute_action(self) -> None:
        temp_dir = tempfile.mkdtemp()

        def remove_temp_dir():
            shutil.rmtree(temp_dir, ignore_errors=True)

        atexit.register(remove_temp_dir)

        logging.debug(f"Downloading latest release of {self.name} to {temp_dir}")
        subprocess.check_call(
            [
                "gh",
                "release",
                "download",
                "--repo",
                self.repository,
                "--pattern",
                self.pattern,
                "--dir",
                temp_dir,
            ]
        )
        # TODO: Implement error handling
        # TODO: Ensure only a single file is found
        for file in Path(temp_dir).glob(self.pattern):
            archive = file
        # TODO: Is there a need to check if its an archive?
        # TODO: Generalize to extract also zip archives
        # TODO: Resolve home directory (and other special path vars?) if it is contained in install_dir
        install_path = Path(self.install_dir)
        file_utils.extract_tar_archive(archive, install_path)
        # TODO: Generalize adding to path
        usr_local_bin = Path("/usr/local/bin")
        file_utils.add_executable_to_path(install_path / "vale", usr_local_bin)

    def get_click_command(self) -> click.Command:
        return click.Command(
            name="install",
            no_args_is_help=False,
            callback=self.execute_action,
            help=f"Install {self.name}.",
        )
