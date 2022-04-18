from __future__ import annotations

import typing as t
from dataclasses import dataclass
from pathlib import Path

from loguru import logger
from rich.console import Console
from rich.console import ConsoleOptions
from rich.console import Group
from rich.console import group
from rich.console import RenderResult
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from dagos.core.components import SoftwareComponent


class SoftwareEnvironmentRegistry(type):
    """A metaclass responsible for registering software environments."""

    environments: t.List[SoftwareEnvironment] = []

    def __call__(cls, *args: t.Any, **kwds: t.Any) -> t.Any:
        """The registry hooks into the object construction lifecycle to register
        software environments.
        """
        environment = super().__call__(*args, **kwds)

        if cls not in cls.environments:
            cls.environments.append(environment)

        return environment

    @classmethod
    def find_environment(cls, name: str) -> t.Optional[SoftwareEnvironment]:
        for environment in cls.environments:
            if environment.name == name:
                return environment
        return None


@dataclass
class Platform:
    os: t.List[str]
    images: t.List[Image]

    def __rich_console__(
        self, console: Console, options: ConsoleOptions
    ) -> t.Generator[RenderResult]:
        parent_table = Table(box=None)
        parent_table.add_column()
        parent_table.add_column()

        os_table = Table(
            title=f"Targeted Operating Systems ({len(self.os)})", min_width=35
        )
        os_table.add_column("Name")
        # os_table.add_column("Packages")
        for os in self.os:
            os_table.add_row(os)

        image_table = Table(title=f"Targeted Container Images ({len(self.images)})")
        image_table.add_column("ID")
        image_table.add_column("Packages")

        for image in self.images:
            package_tree = Tree(
                image.package_manager if image.package_manager else "system"
            )
            for package in image.packages:
                package_tree.add(package)
            image_table.add_row(image.id, package_tree)

        parent_table.add_row(os_table, image_table)
        yield parent_table


@dataclass
class Image:
    id: str
    package_manager: t.Optional[str]
    packages: t.List[str]


@dataclass
class Component:
    name: str
    purpose: t.Optional[str]
    version: t.Optional[str]
    software_component: t.Optional[SoftwareComponent]


class SoftwareEnvironment(metaclass=SoftwareEnvironmentRegistry):
    """Base class for software environments."""

    path: Path
    name: str
    description: t.Optional[str]
    platform: Platform
    components: t.List[Component]

    def __init__(
        self,
        path: Path,
        name: str,
        description: t.Optional[str],
        platform: Platform,
        components: t.List[Component],
    ) -> None:
        """"""
        self.path = path
        self.name = name
        self.description = description
        self.platform = platform
        self.components = components

    def collect_components(self) -> t.List[SoftwareComponent]:
        collected_components: t.List[SoftwareComponent] = []
        unknown_components: t.List[str] = []
        for component in self.components:
            if component.software_component:
                logger.trace("Requested component '{}' is known!", component.name)
                # TODO: Check if selected platform supports component?
                collected_components.append(component.software_component)
            else:
                unknown_components.append(component.name)

        if len(unknown_components) > 0:
            logger.error(
                "{} of the {} requested components are unknown, specifically: {}",
                len(unknown_components),
                len(self.components),
                ", ".join(unknown_components),
            )

        return collected_components

    def __rich__(self) -> Panel:
        @group()
        def get_renderables():
            yield Markdown(f"{self.description}\n")
            yield self.platform

            table = Table(
                title=f"Software Components ({len(self.components)})",
                title_justify="left",
                show_lines=True,
                expand=True,
            )
            table.add_column("Name")
            table.add_column("Purpose", ratio=1)
            table.add_column("Version", justify="right")
            table.add_column("Found?", justify="center")
            table.add_column("Valid?", justify="center")
            for component in self.components:
                table.add_row(
                    component.name,
                    component.purpose,
                    component.version,
                    ":white_check_mark:"
                    if component.software_component
                    else ":cross_mark:",
                    ":white_check_mark:"
                    if component.software_component.is_valid()
                    else ":cross_mark:",
                )
            yield table

        return Panel(
            Group(get_renderables()),
            title=f"Environment: {self.name}",
            title_align="left",
            subtitle=f"Path: {self.path}",
            subtitle_align="right",
        )
