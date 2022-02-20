import typing as t
from io import StringIO
from pathlib import Path


class DagosConfiguration:
    verbosity: int = 0
    component_search_paths: t.List[Path] = [
        # user
        Path.home() / ".dagos" / "components",
        # system (linux)
        Path("/opt/dagos/components"),
        # dagos
        Path(__file__).parent.parent / "components",
    ]

    @classmethod
    def get_config_keys(cls) -> t.List[str]:
        return [x for x in cls.__dict__.keys() if not x.startswith("__")]

    def __repr__(self) -> str:
        result = StringIO()
        result.write("DagosConfiguration{")
        result.write(f"verbosity={self.verbosity}, ")
        result.write(
            f"component_search_paths={','.join([str(x) for x in self.component_search_paths])}"
        )
        result.write("}")
        return result.getvalue()
