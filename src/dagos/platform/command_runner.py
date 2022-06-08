import subprocess
import typing as t
from abc import ABC
from abc import abstractmethod

from loguru import logger

import dagos.containers.buildah as buildah
from dagos.exceptions import DagosException
from dagos.logging import LogLevel


class CommandRunner(ABC):
    @abstractmethod
    def run(
        self,
        command: t.Union[str, t.List[str]],
        user: t.Optional[str] = None,
        capture_stdout: t.Optional[bool] = False,
        capture_stderr: t.Optional[bool] = False,
        ignore_failure: t.Optional[bool] = False,
        log_level: t.Optional[LogLevel] = LogLevel.INFO,
    ) -> subprocess.CompletedProcess:
        pass

    def check_command(self, command: str, user: t.Optional[str] = None) -> bool:
        """Check if provided command is available.

        Args:
            command (str): The command to check availability for.
            user (t.Optional[str], optional): The user[:group] to check for. Defaults to None.

        Returns:
            bool: True, if the command is available, false otherwise.
        """
        args = {
            "user": user,
            "capture_stdout": True,
            "capture_stderr": True,
            "ignore_failure": True,
        }
        # Check that the 'command' executable is on path
        if self.run("command", **args).returncode == 0:
            result = self.run(f"command -v {command}", **args)
        else:
            result = self.run(f"which {command}", **args)
        return result.returncode == 0


class LocalCommandRunner(CommandRunner):
    def run(
        self,
        command: t.Union[str, t.List[str]],
        user: t.Optional[str] = None,
        capture_stdout: t.Optional[bool] = False,
        capture_stderr: t.Optional[bool] = False,
        ignore_failure: t.Optional[bool] = False,
        log_level: t.Optional[LogLevel] = LogLevel.INFO,
    ) -> subprocess.CompletedProcess:
        logger.log(
            log_level.value,
            "Running command: {}",
            command if isinstance(command, str) else " ".join(command),
        )

        if user is not None:
            logger.warning(
                "Local commands are run by the current user, running as a different user is not suppoted at this point."
            )

        result = subprocess.run(
            command,
            shell=True if isinstance(command, str) else False,
            stdout=subprocess.PIPE if capture_stdout else None,
            stderr=subprocess.PIPE if capture_stderr else None,
            text=True,
        )

        if not ignore_failure and result.returncode != 0:
            raise DagosException(f"Command failed with code {result.returncode}!")
        return result


class ContainerCommandRunner(CommandRunner):
    def __init__(self, container: str) -> None:
        self.container = container

    def run(
        self,
        command: t.Union[str, t.List[str]],
        user: t.Optional[str] = None,
        capture_stdout: t.Optional[bool] = False,
        capture_stderr: t.Optional[bool] = False,
        ignore_failure: t.Optional[bool] = False,
        log_level: t.Optional[LogLevel] = LogLevel.INFO,
    ) -> subprocess.CompletedProcess:
        return buildah.run(
            self.container,
            command,
            user,
            capture_stdout,
            capture_stderr,
            ignore_failure,
            log_level,
        )
