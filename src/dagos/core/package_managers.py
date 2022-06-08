from __future__ import annotations

import os
import textwrap
import typing as t

from dagos.platform.command_runner import CommandRunner


class PackageManagerRegistry(type):
    """A metaclass responsible for registering supported package managers."""

    managers: t.List[PackageManager] = []

    def __call__(cls, *args: t.Any, **kwds: t.Any) -> t.Any:
        manager = super().__call__(*args, **kwds)

        if cls not in cls.managers:
            cls.managers.append(manager)

        return manager

    @classmethod
    def find(cls, name: str) -> t.Optional[PackageManager]:
        for manager in cls.managers:
            # TODO: Use a classproperty from boltons?
            if manager.name() == name:
                return manager
        return None


class PackageManager(metaclass=PackageManagerRegistry):
    """A base class for all supported package managers.

    Since the package manager may reside on a remote platform, e.g., within a
    container image, implementing classes should not interact with the system
    themselves but rather return commands to influence it."""

    @classmethod
    def name(cls) -> str:
        """The name of the package manager, defaults to the lower case class name."""
        return str(cls.__name__).lower()

    def install(self, packages: t.List[str], command_runner: CommandRunner) -> None:
        """Install the provided packages via the provided command_runner.

        Args:
            packages (t.List[str]): A list of packages to install.
            command_runner (CommandRunner): A command runner instance to use for installing.
        """
        # TODO: Check root privileges? Enable/disable via flag in class?
        raise NotImplementedError

    def clean(self, command_runner: CommandRunner) -> None:
        """Generate command line call for cleaning any redundant files of this
        manager."""
        return None

    def refresh(self, command_runner: CommandRunner) -> None:
        """Refresh metadata from remote repository."""
        raise NotImplementedError


class Apt(PackageManager):
    def install(self, packages: t.List[str], command_runner: CommandRunner) -> None:
        self.refresh(command_runner)
        command_runner.run(
            f"apt install -y --no-install-recommends {' '.join(packages)}"
        )

    def clean(self, command_runner: CommandRunner) -> None:
        command_runner.run("apt clean")

    def refresh(self, command_runner: CommandRunner) -> None:
        command_runner.run("apt update")


class Dnf(PackageManager):
    def install(self, packages: t.List[str], command_runner: CommandRunner) -> None:
        command_runner.run(f"dnf install -y {' '.join(packages)}")

    def clean(self, command_runner: CommandRunner) -> None:
        command_runner.run("dnf clean all")


class Yum(PackageManager):
    def install(self, packages: t.List[str], command_runner: CommandRunner) -> None:
        command_runner.run(f"yum install -y {' '.join(packages)}")


class Pip(PackageManager):
    def install(self, packages: t.List[str], command_runner: CommandRunner) -> None:
        # TODO: How to handle different python versions?
        command_runner.run(f"pip install {' '.join(packages)}")


class Choco(PackageManager):
    def install(self, packages: t.List[str], command_runner: CommandRunner) -> None:
        command_runner.run(f"choco install --yes {' '.join(packages)}")


class Sdkman(PackageManager):
    @classmethod
    def name(cls) -> str:
        return "sdk"

    def install(self, packages: t.List[str], command_runner: CommandRunner) -> None:
        # In order to use sdk from the command line one needs to source its init script.
        # This is not possible through the subprocess module. Therefore we use a temporary
        # bash script in its stead.
        tmp_file = f"/tmp/sdk-install-script-{os.getpid()}.sh"
        script = textwrap.dedent(
            f"""\
            #!/bin/bash
            source $HOME/.sdkman/bin/sdkman-init.sh
            """
        )
        for package in packages:
            script += f"sdk install {package}\n"
        command_runner.run(f"""bash -c 'echo "{script}" > {tmp_file}'""")
        command_runner.run(f"chmod +x {tmp_file}")
        command_runner.run(f".{tmp_file}")
        command_runner.run(f"rm {tmp_file}")


Apt()
Dnf()
Yum()
Sdkman()
