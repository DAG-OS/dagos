import importlib.util
import inspect
import logging
import typing as t
from pathlib import Path

from dagos.core.components import SoftwareComponent
from dagos.platform.exceptions import UnsupportedPlatformException


class SoftwareComponentScanner(object):
    def scan(self, search_paths: t.List[Path]) -> None:
        logging.trace(f"Looking for software components in {len(search_paths)} places")
        for search_path in search_paths:
            if self._is_valid_search_path(search_path):
                # TODO: Aggregate files for components
                self._scan_search_path(search_path)

    def _scan_search_path(self, search_path: Path) -> None:
        logging.trace(f"Looking for software components in '{search_path}'")
        for folder in search_path.iterdir():
            if self._contains_software_component(folder):
                logging.trace(f"Found folder for software component '{folder.name}'")
                self._scan_folder(folder)

    def _scan_folder(self, folder: Path) -> None:
        for file in folder.iterdir():
            if file.is_file and file.suffix == ".py":
                module_name = f"dagos.components.external.{folder.name}"
                module = self._load_module(module_name, file)
                classes = inspect.getmembers(module, inspect.isclass)
                self._find_software_components(classes)

    def _find_software_components(self, classes: t.List[t.Tuple[str, object]]) -> None:
        for clazz in classes:
            if clazz[0] != "SoftwareComponent" and issubclass(
                clazz[1], SoftwareComponent
            ):
                try:
                    component = clazz[1]()
                except Exception as e:
                    # TODO: Gracefully handle broken plugins
                    logging.warning(f"Failed to instantiate software component: {e}")
                logging.trace(f"Found software component '{component.name}'")

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
                logging.trace(f"Unhandled ModuleNotFoundError!")
                raise UnsupportedPlatformException(e)
        except UnsupportedPlatformException as e:
            logging.debug(
                f"Module '{name}' at '{file}' does not support current platform: {e}"
            )
        return module

    def _is_valid_search_path(self, search_path: Path) -> bool:
        if not search_path.exists():
            logging.trace(f"Component search path '{search_path}' does not exist")
            return False
        return True

    def _contains_software_component(self, path: Path) -> bool:
        if not path.is_dir():
            return False
        if path.name.startswith("__"):
            return False
        return True
