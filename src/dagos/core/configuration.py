import typing as t
from dataclasses import dataclass
from pathlib import Path

import yaml
from loguru import logger

from dagos.exceptions import DagosException


@dataclass
class DagosConfiguration:
    verbosity: int = 0


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

        for variable in vars(self.configuration):
            if variable in yaml_content:
                self.configuration.__dict__[variable] = yaml_content[variable]

        return self.configuration
