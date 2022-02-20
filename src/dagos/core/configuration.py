import typing as t
from io import StringIO
from pathlib import Path


class DagosConfiguration:

    # The level of verbosity used for logging configuration. Lowest is 0 (INFO),
    # highest is 2 (TRACE). Anything higher equals 2.
    verbosity: int = 0
    # The paths where to search for configuration, components, and environments.
    search_paths: t.List[Path] = [
        # User
        Path.home() / ".dagos",
        # System (linux)
        Path("/opt/dagos"),
        # dagos internal
        Path(__file__).parent.parent,
    ]
    # Additional component search paths. Each entry must be a folder which is
    # either named "components" or contains a ".dagos-components" marker file.
    component_search_paths: t.List[Path] = []

    @classmethod
    def get_config_keys(cls) -> t.List[str]:
        return [x for x in cls.__dict__.keys() if not x.startswith("__")]

    def get_component_search_paths(self) -> t.List[Path]:
        paths = []
        paths.extend(self.component_search_paths)
        paths.extend([Path(x) / "components" for x in self.search_paths])
        return paths

    def __repr__(self) -> str:
        result = StringIO()
        result.write("DagosConfiguration{")
        result.write(f"verbosity={self.verbosity}, ")
        result.write(f"search_paths={','.join([str(x) for x in self.search_paths])}, ")
        result.write(
            f"component_search_paths={','.join([str(x) for x in self.component_search_paths])}"
        )
        result.write("}")
        return result.getvalue()
