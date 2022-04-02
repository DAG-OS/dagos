import importlib.util
import inspect
import re
import typing as t
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

from loguru import logger

from dagos.commands.github import GitHubInstallCommand
from dagos.core.commands import CommandRegistry
from dagos.core.commands import CommandType
from dagos.core.components import SoftwareComponent
from dagos.core.validator import Validator
from dagos.exceptions import SchemaValidationException
from dagos.exceptions import ValidationException
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


class SoftwareComponentScanner:

    scan_result: t.Dict[str, ComponentResult] = {}

    def scan(self, search_paths: t.List[Path]) -> None:
        logger.trace("Looking for software components in {} places", len(search_paths))
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
        logger.trace("Looking for software components in '{}'", search_path)
        for folder in search_path.iterdir():
            if self._contains_software_component(folder):
                if not folder.name in self.scan_result:
                    self.scan_result[folder.name] = ComponentResult()
                    logger.trace(
                        "[bold]{}[/bold]: Looking for a software component", folder.name
                    )
                else:
                    logger.trace(
                        "[bold]{}[/bold]: Found additional folder", folder.name
                    )
                scan = self.scan_result[folder.name]
                scan.folders.append(folder)
                self._scan_folder(folder, scan)

    def _scan_folder(self, folder: Path, scan: ComponentResult) -> None:
        for file in [
            x for x in folder.iterdir() if x.is_file() and not x.name.startswith("_")
        ]:
            scan.files.append(file)

            if file.suffix in [".yml", ".yaml"]:
                self._parse_yaml_file(folder.name, file, scan)
            elif file.suffix == ".py" and scan.component is None:
                # TODO: What if there are multiple SoftwareComponents in the py files?
                module_name = f"dagos.components.external.{folder.name}"
                module = self._load_module(folder.name, module_name, file)
                classes = inspect.getmembers(module, inspect.isclass)
                self._find_software_component(folder.name, classes, scan)

    def _find_software_component(
        self,
        component_name: str,
        classes: t.List[t.Tuple[str, object]],
        scan: ComponentResult,
    ) -> None:
        for clazz in classes:
            if clazz[0] != "SoftwareComponent" and issubclass(
                clazz[1], SoftwareComponent
            ):
                try:
                    component = clazz[1]()
                    component.folders = scan.folders
                    component.files = scan.files
                    scan.component = component
                    logger.trace(
                        "[bold]{}[/bold]: Found software component", component_name
                    )
                except Exception as e:
                    # TODO: Gracefully handle broken plugins
                    logger.warning(
                        "[bold]{}[/bold]: Failed to instantiate\n{}", component_name, e
                    )
                return

    def _load_module(self, component: str, name: str, file: Path):
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
                "[bold]{}[/bold]: Module '{}' at '{}' does not support current platform: {}",
                component,
                name,
                file,
                e,
            )
        return module

    def _parse_yaml_file(
        self, component_name: str, file: Path, scan: ComponentResult
    ) -> None:
        content = file.read_text()

        # Regexes constructed via melody, see `src/dagos/core/regexes`.
        if re.match(r"(?:(?:^#.*(?:\n)*)*|(?:^\-\-\-\n){1})command:\n", content):
            self._parse_command_file(component_name, file, scan)
        else:
            logger.debug(
                "[bold]{}[/bold]: Skipping file '{}' with unknown contents",
                component_name,
                file,
            )

    def _parse_command_file(
        self, component_name: str, file: Path, scan: ComponentResult
    ) -> None:
        try:
            data = Validator().validate_command(file)
            command = data["command"]
            command_type = command["type"]
            command_provider = command["provider"]
            configuration = command["configuration"]
            logger.debug(
                "[bold]{}[/bold]: Found {} command based on {}",
                component_name,
                command_type,
                command_provider,
            )
            scan.commands.append(
                CommandResult(file, command_provider, command_type, configuration)
            )
        except SchemaValidationException as e:
            logger.warning(
                "Invalid command configuration detected at '{}': {}", file, e
            )
        except ValidationException as e:
            logger.warning(e)

    def _construct_command(
        self, component: SoftwareComponent, command_result: CommandResult
    ) -> None:
        logger.trace(
            "[bold]{}[/bold]: Constructing {} command with '{}' provider",
            component.name,
            command_result.type,
            command_result.provider,
        )
        if command_result.provider == "github":
            if command_result.type == "install":
                command = GitHubInstallCommand.parse(command_result.config, component)
                component.add_command(command)
                return
        logger.warning(
            "[bold]{}[/bold]: Unknown command provider '{}' in '{}'!",
            component.name,
            command_result.provider,
            command_result.file,
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
