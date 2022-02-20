import atexit
import fnmatch
from pathlib import Path

import requests
import yaml
from loguru import logger

from dagos.core.commands import Command, CommandType
from dagos.core.components import SoftwareComponent
from dagos.exceptions import DagosException, SoftwareComponentScanException
from dagos.utils import file_utils


class GitHubInstallCommand(Command):
    """Install a software component via a GitHub release."""

    # TODO: Allow providing these values via configuration
    name: str
    repository: str
    pattern: str
    install_dir: str
    binary: str
    strip_root_folder: bool = False

    def __init__(self, parent: SoftwareComponent) -> None:
        super().__init__(CommandType.INSTALL, parent)

    @staticmethod
    def parse(path: Path):
        if not path.exists():
            raise SoftwareComponentScanException("Action file does not exist")
        try:
            with path.open() as f:
                yaml_content = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise SoftwareComponentScanException("YAML is invalid", e)

        command = GitHubInstallCommand()
        # TODO: Add error handling
        command.name = yaml_content["name"]
        command.repository = yaml_content["repository"]
        command.pattern = yaml_content["pattern"]
        command.install_dir = yaml_content["install_dir"]
        if "binary" in yaml_content:
            command.binary = yaml_content["binary"]
        if "strip_root_folder" in yaml_content:
            command.strip_root_folder = yaml_content["strip_root_folder"]
        else:
            command.strip_root_folder = False
        return command

    def _parse_repository_url(self) -> str:
        """
        The provided repository should either include the whole URL,
        i.e., https://github.com/<slug> or github.com/<slug>, or only the slug,
        i.e., <slug>.

        The slug is everything after the github.com part when pointing to the
        main page of a repository.
        """
        if "github.com" in self.repository:
            repository_slug = self.repository.partition("github.com/")[2]
        else:
            repository_slug = self.repository
        return f"""https://api.github.com/repos/{repository_slug}/releases/latest"""

    def _parse_matching_asset(self, release_json):
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
            if fnmatch.fnmatch(asset["name"], self.pattern):
                matching_assets.append(asset)
        asset_count = len(matching_assets)
        logger.debug(f"Found {asset_count} assets")
        if asset_count == 0:
            raise DagosException("Found zero matching assets for provided pattern!")
        if asset_count > 1:
            raise DagosException("Found too many matching assets for provided pattern!")
        return matching_assets[0]

    def execute(self) -> None:
        # TODO: Check if root privileges are required
        logger.debug("Querying GitHub for latest release")
        url = self._parse_repository_url()
        response = requests.get(url)
        release_json = response.json()

        logger.debug("Parsing API response for matching asset")
        asset = self._parse_matching_asset(release_json)

        # TODO: Print how long ago it was published (look at timeago?)
        logger.info(
            f"Downloading release {release_json['name']} published at {release_json['published_at']}"
        )
        archive = file_utils.download_file(asset["browser_download_url"])
        atexit.register(lambda: archive.unlink())

        # TODO: Is there a need to check if its an archive?
        install_path = Path(self.install_dir).resolve()
        file_utils.extract_archive(archive, install_path, self.strip_root_folder)

        self.post_extraction(install_path)

        if hasattr(self, "binary"):
            # TODO: Generalize adding to path
            usr_local_bin = Path("/usr/local/bin")
            file_utils.add_executable_to_path(install_path / self.binary, usr_local_bin)

    def post_extraction(self, install_path: Path) -> None:
        """Called after the downloaded archive is extracted. May be used by
        extending commands to do something with the extracted files before
        remaining things are done.
        """
