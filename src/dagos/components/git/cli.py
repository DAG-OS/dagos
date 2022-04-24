import typing as t
from pathlib import Path

import yaml
from loguru import logger

from dagos.core.commands import ConfigureCommand
from dagos.core.commands import InstallCommand
from dagos.core.components import SoftwareComponent
from dagos.platform import PlatformIssue
from dagos.platform import PlatformSupportChecker

try:
    import ansible_runner
except ImportError:
    pass

inventory = "localhost ansible_connection=local"
roles_path = Path.home() / ".ansible" / "roles"


class GitSoftwareComponent(SoftwareComponent):
    """Install or configure Git on your machine."""

    def __init__(self) -> None:
        super().__init__("git")
        self.add_command(InstallGitCommand(self))
        self.add_command(ConfigureGitCommand(self))

    def supports_platform(self) -> t.List[PlatformIssue]:
        return (
            PlatformSupportChecker()
            .check_module_is_available(
                "ansible_runner",
                description="The ansible extras are not installed!",
                fix_instructions="Install DAG-OS with 'ansible' extras!",
            )
            .issues
        )


class InstallGitCommand(InstallCommand):
    def __init__(self, parent: SoftwareComponent) -> None:
        super().__init__(parent)

    def execute(self) -> None:
        logger.info("Installing Git")
        ansible_runner.run(
            role="dagos.git",
            roles_path=str(roles_path),
            extravars={"state": "install"},
            inventory=inventory,
        )


class ConfigureGitCommand(ConfigureCommand):
    def __init__(self, parent: SoftwareComponent) -> None:
        super().__init__(parent)

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
