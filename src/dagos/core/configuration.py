import typing as t
from io import StringIO
from pathlib import Path

import yaml
from loguru import logger

from dagos.exceptions import DagosException


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


class ConfigurationScanner:

    configuration: DagosConfiguration
    file_name = ".dagos-config.yml"
    search_paths: t.List[Path] = [
        # current dir
        Path.cwd(),
        # user home
        Path.home() / ".dagos",
        # system (linux)
        Path("/opt/dagos"),
    ]

    def __init__(self):
        self.configuration = DagosConfiguration()

    def scan(self) -> DagosConfiguration:
        logger.trace(
            f"Looking for configuration files in {len(self.search_paths)} places"
        )
        for search_path in self.search_paths:
            logger.trace(f"Looking for configuration file in '{search_path}'")
            file = search_path / self.file_name
            if file.exists() and file.is_file():
                logger.debug(f"Found configuration file '{file}'")
                return self.load_configuration(file)
        logger.debug("No configuration file found in search paths, using defaults")
        return self.configuration

    def load_configuration(self, config_file: Path) -> DagosConfiguration:
        logger.debug(f"Loading configuration from '{config_file}'")
        if not config_file.exists():
            raise DagosException("Provided config file does not exist")
        try:
            with config_file.open() as f:
                yaml_content = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise DagosException("YAML is invalid", e)

        for variable in DagosConfiguration.get_config_keys():
            if variable in yaml_content:
                config_value = yaml_content[variable]
                if variable == "component_search_paths":
                    config_value = self._parse_component_search_paths(config_value)

                self.configuration.__dict__[variable] = config_value

        logger.debug(self.configuration)
        return self.configuration

    def _parse_component_search_paths(
        self, additional_search_paths: t.List[str]
    ) -> t.List[Path]:
        intermediary = [Path(x).expanduser() for x in additional_search_paths]
        intermediary.extend(self.configuration.component_search_paths)
        config_value = []
        [config_value.append(x) for x in intermediary if x not in config_value]
        return config_value
