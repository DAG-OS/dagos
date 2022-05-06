from pathlib import Path

from loguru import logger

from dagos.commands.github import GitHubInstallCommand
from dagos.core.components import SoftwareComponent


class StructurizrSoftwareComponent(SoftwareComponent):
    """
    Manage the Structurizr CLI.

    Project home: <https://github.com/structurizr/cli>
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
        self.install_dir = "~/software/structurizr/cli"
        self.binary = "structurizr"

    def post_extraction(self, install_path: Path) -> None:
        """Apply workaround described here:
        https://github.com/structurizr/cli/issues/43
        """
        original_starter = install_path / "structurizr.sh"
        modified_starter = install_path / "structurizr"

        logger.debug("Modifying starter script to work for symlinks")
        content = original_starter.read_text()
        content = content.replace(r"${BASH_SOURCE[0]}", '$(readlink -f "$0")')
        modified_starter.write_text(content)
        modified_starter.chmod(755)
