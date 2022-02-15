from pathlib import Path

import ansible_runner
import yaml
from loguru import logger

from dagos.core.commands import Command, CommandType
from dagos.core.components import SoftwareComponent

inventory = "localhost ansible_connection=local"
roles_path = Path.home() / ".ansible" / "roles"


class GitSoftwareComponent(SoftwareComponent):
    """Install or configure Git on your machine."""

    def __init__(self) -> None:
        super().__init__("git")
        self.add_command(InstallGitCommand(self))


class InstallGitCommand(Command):
    def __init__(self, parent: SoftwareComponent) -> None:
        super().__init__(CommandType.INSTALL, parent)

    def execute(self) -> None:
        logger.info("Installing Git")
        ansible_runner.run(
            role="dagos.git",
            roles_path=str(roles_path),
            extravars={"state": "install"},
            inventory=inventory,
        )


class ConfigureGitCommand(Command):
    def __init__(self, parent: SoftwareComponent) -> None:
        super().__init__(CommandType.CONFIGURE, parent)

    def execute(self) -> None:
        logger.info("Configuring Git")

        extravars = {
            "state": "configure",
        }

        git_config_file = self.parent.get_file("config.yml")
        if git_config_file:
            with open(git_config_file) as f:
                config_values = yaml.safe_load(f)
            if config_values["git_settings"]:
                extravars["git_settings"] = config_values["git_settings"]

        ansible_runner.run(
            role="dagos.git",
            roles_path=str(roles_path),
            extravars=extravars,
            inventory=inventory,
        )
