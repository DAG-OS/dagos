from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path

import click


class ActionType(Enum):
    INSTALL = "install"


# TODO: Action provider?
# TODO: Default installation dir?
class Action(ABC):
    type: ActionType

    @staticmethod
    @abstractmethod
    def parse_action(path: Path):
        pass

    @abstractmethod
    def execute_action(self) -> None:
        pass

    @abstractmethod
    def get_click_command(self) -> click.Command:
        pass
