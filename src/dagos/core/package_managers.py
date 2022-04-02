from __future__ import annotations

import typing as t


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
    def name(cls):
        """The name of the package manager, defaults to the lower case class name."""
        return str(cls.__name__).lower()

    def install(self, packages: t.List[str]) -> str:
        """Generate command line call for installing the provided packages.

        Args:
            packages (t.List[str]): A list of packages to install.

        Returns:
            str: The command line to run for installing provided packages.
        """
        # TODO: Check root privileges? Enable/disable via flag in class?
        raise NotImplementedError

    def clean(self) -> t.Optional[str]:
        """Generate command line call for cleaning any redundant files of this
        manager."""
        return None

    def refresh(self) -> str:
        """Refresh metadata from remote repository."""
        raise NotImplementedError


class Apt(PackageManager):
    def install(self, packages: t.List[str]) -> t.List[str]:
        return [
            self.refresh(),
            f"apt install -y --no-install-recommends {' '.join(packages)}",
        ]

    def clean(self) -> t.Optional[str]:
        return "apt clean"

    def refresh(self):
        return "apt update"


class Dnf(PackageManager):
    def install(self, packages: t.List[str]) -> str:
        return f"dnf install -y {' '.join(packages)}"

    def clean(self) -> t.Optional[str]:
        return "dnf clean all"


class Yum(PackageManager):
    def install(self, packages: t.List[str]) -> str:
        return f"yum install -y {' '.join(packages)}"


class Pip(PackageManager):
    def install(self, packages: t.List[str]) -> str:
        # TODO: How to handle different python versions?
        return f"pip install {' '.join(packages)}"


class Choco(PackageManager):
    def install(self, packages: t.List[str]) -> str:
        return f"choco install --yes {' '.join(packages)}"


Apt()
Dnf()
Yum()
