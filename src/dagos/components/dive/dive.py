import typing as t

from dagos.commands.github import GitHubInstallCommand
from dagos.core.components import SoftwareComponent
from dagos.platform import OperatingSystem
from dagos.platform import PlatformIssue
from dagos.platform import PlatformSupportChecker


class DiveSoftwareComponent(SoftwareComponent):
    """
    Manage dive, a tool for analyzing container images.

    Project home: <https://github.com/wagoodman/dive>
    """

    def __init__(self) -> None:
        super().__init__("dive")
        self.add_command(InstallDiveCommand(self))

    def supports_platform(self) -> t.List[PlatformIssue]:
        return (
            PlatformSupportChecker()
            .check_operating_system([OperatingSystem.LINUX])
            .issues
        )


class InstallDiveCommand(GitHubInstallCommand):
    """Install dive."""

    def __init__(self, parent: SoftwareComponent) -> None:
        super().__init__(parent)
        self.repository = "wagoodman/dive"
        self.pattern = "dive*linux*.tar.gz"
        self.install_dir = "~/software/dive"
        self.binary = "dive"
