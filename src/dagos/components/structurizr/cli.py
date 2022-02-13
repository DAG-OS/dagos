from dagos.commands.github import GitHubInstallCommand
from dagos.core.components import SoftwareComponent


class StructurizrSoftwareComponent(SoftwareComponent):
    """Manage Structurizr CLI.

    Project home: https://github.com/structurizr/cli
    """

    def __init__(self) -> None:
        super().__init__("structurizr")

        install = GitHubInstallCommand(self)
        install.repository = "structurizr/cli"
        install.pattern = "*.zip"
        install.install_dir = "/home/dev/software/structurizr/cli"
        # TODO: Make structurizr CLI executable and put it on the path
        self.add_command(install)
