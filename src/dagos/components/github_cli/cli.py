from dagos.core.components import SoftwareComponent
from dagos.platform import OperatingSystem
from dagos.platform import platform_utils

platform_utils.assert_operating_system([OperatingSystem.LINUX])


class GitHubCliSoftwareComponent(SoftwareComponent):
    """
    Manage the GitHub CLI.

    The GitHub CLI is useful for interacting with GitHub from the command line.

    Project home: <https://github.com/cli/cli>
    """

    def __init__(self) -> None:
        super().__init__("github-cli")
