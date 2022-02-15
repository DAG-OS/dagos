from dagos.commands.github import GitHubInstallCommand
from dagos.core.components import SoftwareComponent


class StructurizrSoftwareComponent(SoftwareComponent):
    """Manage the Structurizr CLI.

    Project home: https://github.com/structurizr/cli
    """

    def __init__(self) -> None:
        super().__init__("structurizr")
        self.add_command(InstallStructurizrCommand(self))


class InstallStructurizrCommand(GitHubInstallCommand):
    """Install the Structurizr CLI."""

    def __init__(self, parent: SoftwareComponent) -> None:
        super().__init__(parent)
        self.repository = "structurizr/cli"
        self.pattern = "*.zip"
        self.install_dir = "/home/dev/software/structurizr/cli"
        # TODO: Make structurizr CLI executable and put it on the path
