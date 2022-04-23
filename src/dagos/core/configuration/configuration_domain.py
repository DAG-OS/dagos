import typing as t
from io import StringIO
from pathlib import Path

import dagos


class DefaultPlaceholder:
    def __init__(self, value: t.Any):
        self.value = value

    def __bool__(self) -> bool:
        return bool(self.value)


DefaultType = t.TypeVar("DefaultType")


def default(value: DefaultType) -> DefaultType:
    """
    You shouldn't use this function directly.
    It's used internally to recognize when a default value has been overwritten, even
    if the new value is `None`.
    """
    return DefaultPlaceholder(value)  # type: ignore


def _get_value(variable):
    return variable.value if _is_default_value(variable) else variable


def _is_default_value(value: t.Any) -> bool:
    return isinstance(value, DefaultPlaceholder)


class DagosConfiguration:
    """A singleton that contains the values of DAG-OS related configuration options.

    For each option it carries the default value which may be overwritten once.
    """

    __instance = None

    def __new__(cls):
        if DagosConfiguration.__instance is None:
            DagosConfiguration.__instance = object.__new__(cls)
        return DagosConfiguration.__instance

    # TODO: Handle environment variables?
    def __init__(
        self,
        verbosity: int = default(0),
        search_paths: t.List[Path] = default(
            [
                # User
                Path.home() / ".dagos",
                # System (linux)
                Path("/opt/dagos"),
                # dagos internal
                Path(dagos.__file__).parent,
            ]
        ),
        component_search_paths: t.List[Path] = default([]),
        environment_search_paths: t.List[Path] = default([]),
    ) -> None:
        self._verbosity = verbosity
        self._search_paths = search_paths
        self._component_search_paths = component_search_paths
        self._environment_search_paths = environment_search_paths

    @property
    def verbosity(self) -> int:
        return _get_value(self._verbosity)

    @verbosity.setter
    def verbosity(self, value: int) -> None:
        if _is_default_value(self._verbosity):
            self._verbosity = value

    @property
    def search_paths(self) -> t.List[Path]:
        return _get_value(self._search_paths)

    @search_paths.setter
    def search_paths(self, value: t.List[Path]):
        if _is_default_value(self._search_paths):
            self._search_paths = value

    @property
    def component_search_paths(self) -> t.List[Path]:
        paths = []
        paths.extend(_get_value(self._component_search_paths))
        paths.extend([Path(x) / "components" for x in self.search_paths])
        return paths

    @component_search_paths.setter
    def component_search_paths(self, value: t.List[Path]):
        if _is_default_value(self._component_search_paths):
            self._component_search_paths = value

    @property
    def environment_search_paths(self) -> t.List[Path]:
        paths = []
        paths.extend(_get_value(self._environment_search_paths))
        paths.extend([Path(x) / "environments" for x in self.search_paths])
        return paths

    @environment_search_paths.setter
    def environment_search_paths(self, value: t.List[Path]):
        if _is_default_value(self._environment_search_paths):
            self._environment_search_paths = value

    @classmethod
    def get_config_keys(cls) -> t.List[str]:
        return [
            x
            for x in cls.__dict__.keys()
            if not x.startswith("__") and x != "get_config_keys"
        ]

    def __repr__(self) -> str:
        result = StringIO()
        result.write("DagosConfiguration{")
        result.write(f"verbosity={self.verbosity}, ")

        search_paths = ",".join([str(x) for x in self.search_paths])
        result.write(f"search_paths={search_paths}, ")

        component_search_paths = ",".join([str(x) for x in self.component_search_paths])
        result.write(f"component_search_paths={component_search_paths}, ")

        environment_search_paths = ",".join(
            [str(x) for x in self.environment_search_paths]
        )
        result.write(f"environment_search_paths={environment_search_paths}")
        result.write("}")
        return result.getvalue()
