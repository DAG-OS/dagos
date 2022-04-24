import subprocess
import typing as t

from loguru import logger

from dagos.core.commands import InstallCommand
from dagos.core.components import SoftwareComponent
from dagos.platform import PlatformIssue
from dagos.platform import PlatformSupportChecker


class SdkmanSoftwareComponent(SoftwareComponent):
    """
    Manage SDKMAN, the Software Development Kit Manager.

    Project home: <https://sdkman.io>
    """

    def __init__(self) -> None:
        super().__init__("sdkman")
        self.add_command(InstallSdkmanCommand(self))

    def supports_platform(self) -> t.List[PlatformIssue]:
        return (
            PlatformSupportChecker()
            .check_command_is_available("bash")
            .check_command_is_available("curl")
            .check_command_is_available("sed")
            .check_command_is_available("unzip")
            .check_command_is_available("zip")
            .issues
        )


class InstallSdkmanCommand(InstallCommand):
    """Install SDKMAN."""

    def __init__(self, parent: SoftwareComponent) -> None:
        super().__init__(parent)

    def execute(self) -> None:
        logger.info("Download and run installer")
        subprocess.run(f"curl -s 'https://get.sdkman.io' | bash", shell=True)
