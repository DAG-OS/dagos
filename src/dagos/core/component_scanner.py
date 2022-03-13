import importlib.util
import inspect
import typing as t
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from loguru import logger

from dagos.commands.github import GitHubInstallCommand
from dagos.core.commands import CommandRegistry, CommandType
from dagos.core.components import SoftwareComponent
from dagos.platform.exceptions import UnsupportedPlatformException


@dataclass
class CommandResult:
    file: Path
    provider: str
    type: CommandType
    config: t.Dict


@dataclass
class ComponentResult:
    component: t.Optional[SoftwareComponent] = None
    commands: t.List[CommandResult] = field(default_factory=list)
    folders: t.List[Path] = field(default_factory=list)
    files: t.List[Path] = field(default_factory=list)


class SoftwareComponentScanner(object):

    scan_result: t.Dict[str, ComponentResult] = {}

    def scan(self, search_paths: t.List[Path]) -> None:
        logger.trace(f"Looking for software components in {len(search_paths)} places")
        for search_path in search_paths:
            if self._is_valid_search_path(search_path):
                self._scan_search_path(search_path)

        # Add found commands to existing components or create new ones when no
        # explicit component is defined
        for name, component_result in self.scan_result.items():
            if len(component_result.commands) > 0:
                if component_result.component is None:
                    component_result.component = SoftwareComponent(
                        name, component_result.folders, component_result.files
                    )
                for command_result in component_result.commands:
                    self._construct_command(component_result.component, command_result)

        # Aggregate component commands into a manage command group
        for component in [
            x.component for x in self.scan_result.values() if not x.component is None
        ]:
            CommandRegistry.add_command(
                CommandType.MANAGE, component.build_manage_command_group()
            )

    def _scan_search_path(self, search_path: Path) -> None:
        logger.trace(f"Looking for software components in '{search_path}'")
        for folder in search_path.iterdir():
            if self._contains_software_component(folder):
                logger.trace(f"Found folder for software component '{folder.name}'")
                if not folder.name in self.scan_result:
                    self.scan_result[folder.name] = ComponentResult()
                self.scan_result[folder.name].folders.append(folder)
                self._scan_folder(folder)

    def _scan_folder(self, folder: Path) -> None:
        for file in [
            x for x in folder.iterdir() if x.is_file() and not x.name.startswith("_")
        ]:
            self.scan_result[folder.name].files.append(file)
            if file.suffix in [".yml", ".yaml"]:
                self._parse_yaml_file(folder.name, file)
            elif file.suffix == ".py":
                # TODO: What if there are multiple SoftwareComponents in the py files?
                module_name = f"dagos.components.external.{folder.name}"
                module = self._load_module(module_name, file)
                classes = inspect.getmembers(module, inspect.isclass)
                self._find_software_component(folder.name, classes)

    def _find_software_component(
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
                    self.scan_result[component_name].component = component
                    logger.trace(f"Found software component '{component.name}'")
                except Exception as e:
                    # TODO: Gracefully handle broken plugins
                    logger.warning(f"Failed to instantiate software component: {e}")
                return

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

    def _parse_yaml_file(self, component_name: str, file: Path) -> None:
        logger.trace(f"Parsing YAML file '{file}'")
        try:
            with file.open() as f:
                yaml_content = yaml.safe_load(f)
        except yaml.YAMLError as e:
            logger.warning(f"Invalid YAML content in file '{file}' detected: {e}")
            return

        if "command" in yaml_content:
            command = yaml_content["command"]
            command_type = command["type"] if "type" in command else None
            command_provider = command["provider"] if "provider" in command else None
            configuration = (
                command["configuration"] if "configuration" in command else None
            )
            if (
                not command_type is None
                and not command_provider is None
                and not configuration is None
            ):
                logger.debug(
                    f"Found {command_type} command for {component_name} based on {command_provider}"
                )
                self.scan_result[component_name].commands.append(
                    CommandResult(file, command_provider, command_type, configuration)
                )

    def _construct_command(
        self, component: SoftwareComponent, command_result: CommandResult
    ) -> None:
        logger.trace(
            f"Constructing {command_result.type} command with '{command_result.provider}' provider for '{component.name}' software component"
        )
        if command_result.provider == "github":
            if command_result.type == "install":
                command = GitHubInstallCommand.parse(command_result.config, component)
                component.add_command(command)
                return
        logger.warning(
            f"Unknown command provider '{command_result.provider}' in '{command_result.file}'!"
        )

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
