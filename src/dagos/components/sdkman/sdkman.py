import subprocess

from loguru import logger

from dagos.core.commands import InstallCommand
from dagos.core.components import SoftwareComponent
from dagos.platform import platform_utils

platform_utils.assert_command_available("bash")
platform_utils.assert_command_available("curl")
platform_utils.assert_command_available("sed")
platform_utils.assert_command_available("unzip")
platform_utils.assert_command_available("zip")


class SdkmanSoftwareComponent(SoftwareComponent):
    """
    Manage SDKMAN, the Software Development Kit Manager.

    Project home: <https://sdkman.io>
    """

    def __init__(self) -> None:
        super().__init__("sdkman")
        self.add_command(InstallSdkmanCommand(self))


class InstallSdkmanCommand(InstallCommand):
    """Install SDKMAN."""

    def __init__(self, parent: SoftwareComponent) -> None:
        super().__init__(parent)

    def execute(self) -> None:
        logger.info("Download and run installer")
        subprocess.run(f"curl -s 'https://get.sdkman.io' | bash", shell=True)
