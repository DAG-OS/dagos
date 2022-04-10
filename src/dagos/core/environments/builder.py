from __future__ import annotations

import typing as t
from pathlib import Path

from .domain import Component
from .domain import Image
from .domain import Platform
from .domain import SoftwareEnvironment
from dagos.core.validator import Validator


class SoftwareEnvironmentBuilder:
    def __init__(self) -> None:
        self._description = None
        self._components = []

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

    def components(self, components: t.List[Component]) -> SoftwareEnvironmentBuilder:
        self._components = components
        return self

    def build(self) -> SoftwareEnvironment:
        return SoftwareEnvironment(
            self._name, self._description, self._platform, self._components
        )

    @classmethod
    def from_file(cls, file: Path) -> SoftwareEnvironment:
        # TODO: Upon schema errors display env as greyed out with errors
        data = Validator().validate_environment(file.expanduser())
        environment: t.Dict = data["environment"]

        builder = (
            SoftwareEnvironmentBuilder()
            .name(environment["name"])
            .description(environment.get("description"))
        )

        # TODO: How does this behave if there is a list or string?
        os = environment["platform"]["os"]
        images = []
        if "images" in environment["platform"]:
            for image in environment["platform"]["images"]:
                images.append(
                    Image(
                        image["id"],
                        image.get("package_manager"),
                        image.get("packages", []),
                    )
                )
        builder.platform(Platform(os, images))
        for component in environment["components"]:
            builder.add_component(
                Component(
                    component["name"],
                    component.get("purpose"),
                    component.get("version"),
                )
            )
        return builder.build()
