from __future__ import annotations

import typing as t
from dataclasses import dataclass
from pathlib import Path

from loguru import logger

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
