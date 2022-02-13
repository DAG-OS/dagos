from dagos.commands.github import GitHubInstallCommand
from dagos.core.components import SoftwareComponent


class ValeSoftwareComponent(SoftwareComponent):
    """Manage Vale."""

    def __init__(self) -> None:
        super().__init__("vale")

        install = GitHubInstallCommand(self)
        install.repository = "https://github.com/errata-ai/vale"
        install.pattern = "vale*Linux_64*.tar.gz"
        install.install_dir = "/home/dev/software/vale"
        install.binary = "vale"
