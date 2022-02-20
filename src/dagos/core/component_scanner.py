import importlib.util
import inspect
import typing as t
from dataclasses import dataclass, field
from pathlib import Path

from loguru import logger

from dagos.core.components import SoftwareComponent
from dagos.platform.exceptions import UnsupportedPlatformException


@dataclass
class ComponentFiles:
    folders: t.List[Path] = field(default_factory=list)
    files: t.List[Path] = field(default_factory=list)


class SoftwareComponentScanner(object):

    scan_result: t.Dict[str, ComponentFiles] = {}

    def scan(self, search_paths: t.List[Path]) -> None:
        logger.trace(f"Looking for software components in {len(search_paths)} places")
        for search_path in search_paths:
            if self._is_valid_search_path(search_path):
                self._scan_search_path(search_path)

    def _scan_search_path(self, search_path: Path) -> None:
        logger.trace(f"Looking for software components in '{search_path}'")
        for folder in search_path.iterdir():
            if self._contains_software_component(folder):
                logger.trace(f"Found folder for software component '{folder.name}'")
                if not folder.name in self.scan_result:
                    self.scan_result[folder.name] = ComponentFiles()
                self.scan_result[folder.name].folders.append(folder)
                self._scan_folder(folder)

    def _scan_folder(self, folder: Path) -> None:
        for file in folder.iterdir():
            if not file.name.startswith("_"):
                self.scan_result[folder.name].files.append(file)
            if file.is_file and file.suffix == ".py":
                module_name = f"dagos.components.external.{folder.name}"
                module = self._load_module(module_name, file)
                classes = inspect.getmembers(module, inspect.isclass)
                self._find_software_components(folder.name, classes)

    def _find_software_components(
        self, component_name: str, classes: t.List[t.Tuple[str, object]]
    ) -> None:
        for clazz in classes:
            if clazz[0] != "SoftwareComponent" and issubclass(
                clazz[1], SoftwareComponent
            ):
                try:
                    component = clazz[1]()
                    component.folders = self.scan_result[component_name].folders
                    component.files = self.scan_result[component_name].files
                except Exception as e:
                    # TODO: Gracefully handle broken plugins
                    logger.warning(f"Failed to instantiate software component: {e}")
                    return
                logger.trace(f"Found software component '{component.name}'")

    def _load_module(self, name: str, file: Path):
        spec = importlib.util.spec_from_file_location(name, file)
        module = importlib.util.module_from_spec(spec)
        try:
            try:
                spec.loader.exec_module(module)
            except ModuleNotFoundError as e:
                if "ansible" in e.msg:
                    raise UnsupportedPlatformException(
                        "Install DAG-OS 'ansible' extras!"
                    )
                logger.trace(f"Unhandled ModuleNotFoundError!")
                raise UnsupportedPlatformException(e)
        except UnsupportedPlatformException as e:
            logger.debug(
                f"Module '{name}' at '{file}' does not support current platform: {e}"
            )
        return module

    def _is_valid_search_path(self, search_path: Path) -> bool:
        if not search_path.exists():
            logger.trace(f"Component search path '{search_path}' does not exist")
            return False
        if not search_path.is_dir():
            logger.warning(f"The search path '{search_path}' is not a folder!")
            return False
        if not search_path.name == "components" and not any(
            search_path.glob(".dagos-components")
        ):
            logger.warning(
                f"The search path '{search_path}' must either be named 'components' or contain a marker file '.dagos-components'"
            )
            return False
        return True

    def _contains_software_component(self, path: Path) -> bool:
        if not path.is_dir():
            return False
        if path.name.startswith("__"):
            return False
        return True
