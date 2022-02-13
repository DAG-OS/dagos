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

        install = GitHubInstallCommand(self)
        # TODO: Allow providing these values via configuration
        install.repository = "cli/cli"
        install.pattern = "gh*linux_amd64.tar.gz"
        install.strip_root_folder = True
        install.install_dir = "/home/dev/software/github_cli"
        install.binary = "bin/gh"

        self.add_command(install)
