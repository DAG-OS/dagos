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


def validate_component(component: SoftwareComponent) -> None:
    if not component.cli.exists():
        raise SoftwareComponentScanException(
            f"Failed to find CLI for '{component.name}' software component!"
        )


def find_components() -> t.Dict[str, SoftwareComponent]:
    logging.trace(
        f"Looking for software components in {len(component_search_paths)} places"
    )
    components = {}
    for search_path in component_search_paths:
        if not search_path.exists():
            logging.trace(f"Component search path '{search_path}' does not exist")
            continue

        logging.trace(f"Looking for software components in '{search_path}'")
        for folder in search_path.iterdir():
            if folder.is_dir():
                if folder.name in components:
                    component = components[folder.name]
                    logging.trace(
                        f"Found another folder for software component '{folder.name}' at '{folder}'"
                    )
                else:
                    component = SoftwareComponent(folder.name)
                    logging.trace(
                        f"Found software component '{folder.name}' at '{folder}'"
                    )
                components[folder.name] = scan_folder_for_component_files(
                    folder, component
                )

    validate_component(component)
    return components


def find_component(name: str) -> SoftwareComponent:
    logging.trace(
        f"Looking for '{name}' software component in {len(component_search_paths)} places"
    )
    component = SoftwareComponent(name)
    for search_path in component_search_paths:
        if not search_path.exists():
            logging.trace(f"Component search path '{search_path}' does not exist")
            continue

        for folder in search_path.iterdir():
            if folder.is_dir() and folder.name == name:
                logging.trace(f"Found '{name}' software component at '{folder}'")
                component = scan_folder_for_component_files(folder, component)

    validate_component(component)
    return component
