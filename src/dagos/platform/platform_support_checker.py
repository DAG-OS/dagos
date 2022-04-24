from __future__ import annotations

import typing as t

import dagos.platform.platform_utils as platform_utils
from .platform_domain import CommandNotAvailableIssue
from .platform_domain import OperatingSystem
from .platform_domain import PlatformIssue
from .platform_domain import UnsupportedOperatingSystemIssue


class PlatformSupportChecker:
    """
    A class to help check if the current platform supports a set of requirements.
    It's used by SoftwareComponents to check if they suppport the current platform.
    """

    issues: t.List[PlatformIssue]

    def __init__(self) -> None:
        self.issues = []

    def check_operating_system(
        self, supported_operating_systems: t.List[OperatingSystem]
    ) -> PlatformSupportChecker:
        for operating_system in supported_operating_systems:
            if platform_utils.is_operating_system(operating_system):
                return self
        self.issues.append(UnsupportedOperatingSystemIssue(supported_operating_systems))
        return self

    def check_command_is_available(
        self,
        command: str,
        fixable: bool = True,
        installation_instructions: t.Optional[str] = None,
    ) -> PlatformSupportChecker:
        if not platform_utils.is_command_available(command):
            self.issues.append(
                CommandNotAvailableIssue(command, fixable, installation_instructions)
            )
        return self

    def check_module_is_available(
        self,
        module: str,
        description: t.Optional[str] = None,
        fixable: bool = True,
        fix_instructions: t.Optional[str] = None,
    ) -> PlatformSupportChecker:
        module_name = module
        try:
            import module
        except ImportError:
            self.issues.append(
                PlatformIssue(
                    description
                    if description
                    else f"Required Python module '{module_name}' is unavailable!",
                    fixable,
                    fix_instructions,
                )
            )
        return self
