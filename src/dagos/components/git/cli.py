import logging
from pathlib import Path

import ansible_runner
import yaml

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
        logging.info("Installing Git")
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
        logging.info("Configuring Git")

        # TODO: Use configuration again
        # if self.parent.config.exists():
        #    with open(self.parent.config) as f:
        #        config_values = yaml.safe_load(f)
        #    if config_values["git_settings"]:
        #        git_settings = config_values["git_settings"]
        extravars = {
            "state": "configure",
            # "git_settings": git_settings,
        }

        ansible_runner.run(
            role="dagos.git",
            roles_path=str(roles_path),
            extravars=extravars,
            inventory=inventory,
        )
