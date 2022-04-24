import typing as t

from dagos.core.components import SoftwareComponent
from dagos.platform import OperatingSystem
from dagos.platform import PlatformIssue
from dagos.platform import PlatformSupportChecker


class GitHubCliSoftwareComponent(SoftwareComponent):
    """
    Manage the GitHub CLI.

    The GitHub CLI is useful for interacting with GitHub from the command line.

    Project home: <https://github.com/cli/cli>
    """

    def __init__(self) -> None:
        super().__init__("github-cli")

    def supports_platform(self) -> t.List[PlatformIssue]:
        return (
            PlatformSupportChecker()
            .check_operating_system([OperatingSystem.LINUX])
            .issues
        )
