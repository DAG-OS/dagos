from dagos.commands.github import GitHubInstallCommand
from dagos.core.components import SoftwareComponent


class DiveSoftwareComponent(SoftwareComponent):
    """Manage dive, a tool for analyzing container images.

    Project home: https://github.com/wagoodman/dive
    """

    def __init__(self) -> None:
        super().__init__("dive")
        self.add_command(InstallDiveCommand(self))


class InstallDiveCommand(GitHubInstallCommand):
    """Install dive."""

    def __init__(self, parent: SoftwareComponent) -> None:
        super().__init__(parent)
        self.repository = "wagoodman/dive"
        self.pattern = "dive*linux*.tar.gz"
        self.install_dir = "~/software/dive"
        self.binary = "dive"
