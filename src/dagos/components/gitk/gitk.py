import subprocess
import typing as t
from pathlib import Path

import click
from loguru import logger

from dagos.core.commands import ConfigureCommand
from dagos.core.components import SoftwareComponent
from dagos.exceptions import DagosException
from dagos.platform import PlatformIssue
from dagos.platform import PlatformSupportChecker


class GitkSoftwareComponent(SoftwareComponent):
    """Manage gitk."""

    def __init__(self) -> None:
        super().__init__("gitk")
        self.add_command(ConfigureGitkCommand(self))

    def supports_platform(self) -> t.List[PlatformIssue]:
        return PlatformSupportChecker().check_command_is_available("git").issues


class ConfigureGitkCommand(ConfigureCommand):
    """Configure gitk to use Dracula dark theme."""

    def __init__(self, parent: SoftwareComponent) -> None:
        super().__init__(parent)

    def build(self, name: t.Optional[str] = None) -> click.Command:
        command = super().build(name)
        command.params.append(
            click.Option(
                ["--install-dir"],
                required=True,
                help="Where to install the gitk configuration.",
            )
        )
        return command

    def execute(self, install_dir: str) -> None:
        logger.debug("Checking if install dir exists")
        install_dir = Path(install_dir).expanduser()
        if not install_dir.exists():
            raise DagosException("Provided install dir does not exist!")

        logger.debug("Clone the dracula/gitk repository")
        git_repo = "https://github.com/dracula/gitk.git"
        repo_dir = install_dir / "gitk"
        if not repo_dir.exists():
            clone_result = subprocess.run(["git", "clone", git_repo, repo_dir])
            if clone_result.returncode != 0:
                raise DagosException("Failed to clone repository!")

        logger.debug("Ensure configuration dir exists")
        config_dir = Path("~/.config/git").expanduser()
        config_dir.mkdir(parents=True, exist_ok=True)

        logger.debug("Configure gitk to use cloned theme")
        symbolic_link = config_dir / "gitk"
        symbolic_link.unlink()
        symbolic_link.symlink_to(install_dir / "gitk/gitk")
