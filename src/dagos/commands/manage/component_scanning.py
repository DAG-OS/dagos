import logging
import typing as t
from pathlib import Path

# TODO: Make this list configurable
component_search_paths = [
    # user
    Path.home() / ".dagos" / "components",
    # system (linux)
    Path("/opt/dagos/components"),
    # dagos
    Path(__file__).parent.parent.parent / "components",
]


class SoftwareComponentScanException(Exception):
    """A base exception for all component scanning errors."""


class SoftwareComponent:
    """A representation of a software component."""

    name: str
    cli: Path
    config: Path

    def __init__(self, name: str) -> None:
        self.name = name

    def validate(self) -> None:
        """Check if the software component is valid.

        Raises:
            SoftwareComponentScanException: Raised if the component is invalid.
        """
        if not self.cli.exists():
            raise SoftwareComponentScanException(
                f"There is no CLI for '{self.name}' software component!"
            )


def scan_folder_for_component_files(folder: Path, component: SoftwareComponent) -> None:
    for component_file in folder.iterdir():
        if not hasattr(component, "cli") and component_file.name == "cli.py":
            logging.trace(
                f"Found CLI for '{component.name}' software component at '{component_file}'"
            )
            component.cli = component_file
        elif not hasattr(component, "config") and component_file.name == "config.yml":
            logging.trace(
                f"Found configuration file for '{component.name}' software component at '{component_file}'"
            )
            component.config = component_file
    return component


def find_components() -> t.Dict[str, SoftwareComponent]:
    logging.trace(
        f"Looking for software components in {len(component_search_paths)} places"
    )
    components = {}
    for search_path in component_search_paths:
        if not is_valid_search_path(search_path):
            continue

        logging.trace(f"Looking for software components in '{search_path}'")
        for path in search_path.iterdir():
            if contains_software_component(path):
                if path.name in components:
                    component = components[path.name]
                    logging.trace(
                        f"Found another folder for software component '{path.name}' at '{path}'"
                    )
                else:
                    component = SoftwareComponent(path.name)
                    logging.trace(f"Found software component '{path.name}' at '{path}'")
                components[path.name] = scan_folder_for_component_files(path, component)

    component.validate()
    return components


def find_component(name: str) -> SoftwareComponent:
    logging.trace(
        f"Looking for '{name}' software component in {len(component_search_paths)} places"
    )
    component = SoftwareComponent(name)
    for search_path in component_search_paths:
        if not is_valid_search_path(search_path):
            continue

        for path in search_path.iterdir():
            if contains_software_component(path) and path.name == name:
                logging.trace(f"Found '{name}' software component at '{path}'")
                component = scan_folder_for_component_files(path, component)

    component.validate()
    return component


def is_valid_search_path(search_path: Path) -> bool:
    if not search_path.exists():
        logging.trace(f"Component search path '{search_path}' does not exist")
        return False
    return True


def contains_software_component(path: Path) -> bool:
    if not path.is_dir():
        return False
    if path.name.startswith("__"):
        return False
    return True
