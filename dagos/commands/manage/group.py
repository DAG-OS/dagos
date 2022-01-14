import click
import logging
import typing as t

from click.core import Command, Context
from pathlib import Path

component_search_paths = [
    # user
    Path.home() / ".dagos" / "components",
    # system (linux)
    Path("/opt/dagos/components"),
    # dagos
    Path(__file__).parent / "components",
]


def find_components() -> t.Dict[str, Path]:
    logging.debug(
        f"Looking for software components in {len(component_search_paths)} places"
    )
    components = {}
    for search_path in component_search_paths:
        if not search_path.exists():
            logging.debug(f"Component search path '{search_path}' does not exist")
            continue

        logging.debug(f"Looking for software components in '{search_path}'")
        for file in search_path.iterdir():
            if file.is_dir():
                if file.name in components:
                    logging.warning(
                        f"Ignoring duplicate software component '{file.name}' at '{file}'"
                    )
                else:
                    logging.debug(f"Found software component '{file.name}' at '{file}'")
                    components[file.name] = file
    return components


class ManageCLI(click.MultiCommand):
    def list_commands(self, ctx: Context) -> t.List[str]:
        ctx.obj = find_components()
        commands = []
        for name in sorted(ctx.obj):
            cli = ctx.obj[name] / "cli.py"
            if cli.exists():
                commands.append(name)
        commands.sort()
        return commands

    def get_command(self, ctx: Context, cmd_name: str) -> t.Optional[Command]:
        if ctx.obj is None:
            ctx.obj = find_components()
        ns = {}
        fn = ctx.obj[cmd_name] / "cli.py"
        with open(fn) as f:
            code = compile(f.read(), fn, "exec")
            eval(code, ns, ns)
        return ns["cli"]


@click.command(cls=ManageCLI)
def manage():
    """
    Manage software components.
    """
    pass
