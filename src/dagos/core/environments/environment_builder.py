from __future__ import annotations

import typing as t
from pathlib import Path

from .environment_domain import Component
from .environment_domain import EnvironmentVariable
from .environment_domain import Image
from .environment_domain import Packages
from .environment_domain import Platform
from .environment_domain import SoftwareEnvironment
from dagos.core.components import SoftwareComponentRegistry
from dagos.core.validator import Validator


class SoftwareEnvironmentBuilder:
    def __init__(self) -> None:
        self._description = None
        self._components = []

    def path(self, path: Path) -> SoftwareEnvironmentBuilder:
        self._path = path
        return self

    def name(self, name: str) -> SoftwareEnvironmentBuilder:
        self._name = name
        return self

    def description(self, description: t.Optional[str]) -> SoftwareEnvironmentBuilder:
        self._description = description
        return self

    def platform(self, platform: Platform) -> SoftwareEnvironmentBuilder:
        self._platform = platform
        return self

    def add_component(self, component: Component) -> SoftwareEnvironmentBuilder:
        self._components.append(component)
        return self

    def build(self) -> SoftwareEnvironment:
        return SoftwareEnvironment(
            self._path, self._name, self._description, self._platform, self._components
        )

    @classmethod
    def from_file(cls, file: Path) -> SoftwareEnvironment:
        # TODO: Upon schema errors display env as greyed out with errors
        data = Validator().validate_environment(file.expanduser())
        environment: t.Dict = data["environment"]

        builder = (
            SoftwareEnvironmentBuilder()
            .path(file)
            .name(environment["name"])
            .description(environment.get("description"))
        )

        env = cls._parse_env(environment["platform"])
        packages = cls._parse_packages(environment["platform"].get("packages"))
        images = cls._parse_images(environment["platform"])
        builder.platform(Platform(env, packages, images))

        for component in environment["components"]:
            builder.add_component(
                Component(
                    component["name"],
                    component.get("purpose"),
                    component.get("version", "latest"),
                    SoftwareComponentRegistry.find_component(component["name"]),
                )
            )
        return builder.build()

    @classmethod
    def _parse_env(cls, platform: t.Dict) -> t.List[EnvironmentVariable]:
        envs = []
        if "env" in platform:
            for env in platform["env"]:
                envs.append(EnvironmentVariable(env.get("name"), env.get("value")))
        return envs

    @classmethod
    def _parse_packages(cls, packages: t.Optional[t.Dict]) -> t.List[Packages]:
        result = []
        if packages is not None and len(packages) > 0:
            if isinstance(packages[0], str):
                result.append(Packages(packages))
            else:
                for entry in packages:
                    result.append(
                        Packages(
                            entry.get("packages"),
                            entry.get("manager", "system"),
                            entry.get("dependency"),
                        )
                    )
        return result

    @classmethod
    def _parse_images(cls, platform: t.Dict) -> t.List[Image]:
        images = []
        if "images" in platform:
            for image in platform["images"]:
                images.append(
                    Image(image["id"], cls._parse_packages(image.get("packages")))
                )
        return images
