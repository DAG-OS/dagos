from dagos.commands.github import GitHubInstallCommand
from dagos.core.components import SoftwareComponent


class ValeSoftwareComponent(SoftwareComponent):
    """Manage Vale."""

    def __init__(self) -> None:
        super().__init__("vale")
        self.add_command(InstallValeCommand(self))


class InstallValeCommand(GitHubInstallCommand):
    """Install Vale."""

    def __init__(self, parent: SoftwareComponent) -> None:
        super().__init__(parent)
        self.repository = "https://github.com/errata-ai/vale"
        self.pattern = "vale*Linux_64*.tar.gz"
        self.install_dir = "/home/dev/software/vale"
        self.binary = "vale"
