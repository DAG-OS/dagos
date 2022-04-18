import typing as t
from pathlib import Path

from loguru import logger

from dagos.core.configuration import DagosConfiguration
from dagos.core.validator import Validator


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
                self.load_configuration(file)
        logger.debug("No configuration file found in search paths, using defaults")
        return self.configuration

    def load_configuration(self, config_file: Path) -> DagosConfiguration:
        logger.debug(f"Loading configuration from '{config_file}'")
        data = Validator().validate_configuration(config_file)
        known_options = DagosConfiguration.get_config_keys()
        for key, value in data.items():
            if key in known_options:
                # TODO: Dynamically set simple values somehow
                if key == "verbosity":
                    self.configuration.verbosity = value
                elif key == "search_paths":
                    self.configuration.search_paths = self._parse_search_paths(value)
                elif key == "component_search_paths":
                    self.configuration.component_search_paths = (
                        self._parse_search_paths(value)
                    )
                elif key == "environment_search_paths":
                    self.configuration.environment_search_paths = (
                        self._parse_search_paths(value)
                    )
            else:
                logger.warning("Unknown configuration option '{}' detected", key)

        logger.debug(self.configuration)

    def _parse_search_paths(self, search_paths: t.List[str]) -> t.List[Path]:
        return [Path(x).expanduser() for x in search_paths]
