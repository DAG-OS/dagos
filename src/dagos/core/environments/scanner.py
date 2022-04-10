import typing as t
from pathlib import Path

from loguru import logger

from .builder import SoftwareEnvironmentBuilder
from dagos.exceptions import ValidationException


class SoftwareEnvironmentScanner:
    def scan(self, search_paths: t.List[Path]) -> None:
        logger.trace(
            "Looking for software environments in {} places", len(search_paths)
        )
        for search_path in search_paths:
            if self._is_valid_search_path(search_path):
                self._scan_search_path(search_path)

    def _scan_search_path(self, search_path: Path) -> None:
        logger.trace("Looking for software environments in '{}'", search_path)
        for path in search_path.iterdir():
            if path.is_file() and path.suffix in [".yml", ".yaml"]:
                try:
                    environment = SoftwareEnvironmentBuilder.from_file(path)
                    logger.trace(
                        "Found the '{}' software environment", environment.name
                    )
                except ValidationException as e:
                    logger.warning("Found invalid software environment", e)
                    continue

    def _is_valid_search_path(self, search_path: Path) -> bool:
        if not search_path.exists():
            logger.trace(f"Environment search path '{search_path}' does not exist")
            return False
        if not search_path.is_dir():
            logger.warning(f"The search path '{search_path}' is not a folder!")
            return False
        return True
