import atexit
import fnmatch
import logging
from pathlib import Path

import click
import requests
import yaml

from dagos.components.domain import Action
from dagos.components.exceptions import SoftwareComponentScanException
from dagos.exceptions import DagosException
from dagos.utils import file_utils


class GitHubCliInstallAction(Action):
    """Install a software component from GitHub using the GitHub CLI."""

    name: str
    repository: str
    pattern: str
    install_dir: str
    binary: str
    strip_root_folder: bool

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
        # TODO: Add error handling
        action.name = yaml_content["name"]
        action.repository = yaml_content["repository"]
        action.pattern = yaml_content["pattern"]
        action.install_dir = yaml_content["install_dir"]
        if "binary" in yaml_content:
            action.binary = yaml_content["binary"]
        if "strip_root_folder" in yaml_content:
            action.strip_root_folder = yaml_content["strip_root_folder"]
        else:
            action.strip_root_folder = False
        return action

    @staticmethod
    def _parse_repository_url(repository: str) -> str:
        """
        The provided repository should either include the whole URL,
        i.e., https://github.com/<slug> or github.com/<slug>, or only the slug,
        i.e., <slug>.

        The slug is everything after the github.com part when pointing to the
        main page of a repository.
        """
        if "github.com" in repository:
            repository_slug = repository.partition("github.com/")[2]
        else:
            repository_slug = repository
        return f"""https://api.github.com/repos/{repository_slug}/releases/latest"""

    @staticmethod
    def _parse_matching_asset(release_json, pattern):
        """Parse the asset matching provided pattern from the API call result.

        Args:
            release_json (json): The complete API call result.
            pattern (glob): A glob pattern to find the wanted asset.

        Raises:
            DagosException: If no matching assets are found.
            DagosException: If too many matching assets are found.

        Returns:
            json: The JSON describing the asset.
        """
        matching_assets = []
        for asset in release_json["assets"]:
            if fnmatch.fnmatch(asset["name"], pattern):
                matching_assets.append(asset)
        asset_count = len(matching_assets)
        logging.debug(f"Found {asset_count} assets")
        if asset_count == 0:
            raise DagosException("Found zero matching assets for provided pattern!")
        if asset_count > 1:
            raise DagosException("Found too many matching assets for provided pattern!")
        return matching_assets[0]

    def execute_action(self) -> None:
        logging.debug("Querying GitHub for latest release")
        url = GitHubCliInstallAction._parse_repository_url(self.repository)
        response = requests.get(url)
        release_json = response.json()

        logging.debug("Parsing API response for matching asset")
        asset = GitHubCliInstallAction._parse_matching_asset(release_json, self.pattern)

        # TODO: Print how long ago it was published (look at timeago?)
        logging.info(
            f"Downloading release {release_json['name']} published at {release_json['published_at']}"
        )
        archive = file_utils.download_file(asset["browser_download_url"])

        def remove_archive():
            archive.unlink()

        atexit.register(remove_archive)

        # TODO: Is there a need to check if its an archive?
        # TODO: Generalize to extract also zip archives
        # TODO: Resolve home directory (and other special path vars?) if it is contained in install_dir
        install_path = Path(self.install_dir)
        file_utils.extract_archive(archive, install_path, self.strip_root_folder)

        if hasattr(self, "binary"):
            # TODO: Generalize adding to path
            usr_local_bin = Path("/usr/local/bin")
            file_utils.add_executable_to_path(install_path / self.binary, usr_local_bin)

    def get_click_command(self) -> click.Command:
        return click.Command(
            name="install",
            no_args_is_help=False,
            callback=self.execute_action,
            help=f"Install {self.name}.",
        )
