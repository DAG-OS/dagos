from __future__ import annotations

import platform
import typing as t
from io import StringIO

if t.TYPE_CHECKING:
    from .platform_domain import OperatingSystem


def build_unsupported_system_message(
    supported_operating_systems: t.List[OperatingSystem] = None,
) -> str:
    message = StringIO()
    message.write(platform.system())
    message.write(" is not supported")
    if supported_operating_systems != None:
        if len(supported_operating_systems) == 1:
            message.write(f", only {supported_operating_systems[0].value} is")
        else:
            message.write(", only one of ")
            message.write(", ".join(x.value for x in supported_operating_systems))
            message.write(" is")
    message.write("!")
    return message.getvalue()
