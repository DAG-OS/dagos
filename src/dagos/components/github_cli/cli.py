import dagos.platform.utils as platform_utils
from dagos.commands.github import GitHubInstallCommand
from dagos.core.components import SoftwareComponent
from dagos.platform.domain import OperatingSystem

platform_utils.assert_operating_system([OperatingSystem.LINUX])


class GitHubCliSoftwareComponent(SoftwareComponent):
    """Manage the GitHub CLI.

    The GitHub CLI is useful for interacting with GitHub from the command line.
    Project home: https://github.com/cli/cli
    """

    def __init__(self) -> None:
        super().__init__("github-cli")
        self.add_command(InstallGitHubCliCommand(self))


class InstallGitHubCliCommand(GitHubInstallCommand):
    """Install the GitHub CLI."""

    def __init__(self, parent: SoftwareComponent) -> None:
        super().__init__(parent)
        self.repository = "cli/cli"
        self.pattern = "gh*linux_amd64.tar.gz"
        self.strip_root_folder = True
        self.install_dir = "/home/dev/software/github_cli"
        self.binary = "bin/gh"
