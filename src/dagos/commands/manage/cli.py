import logging
import typing as t

import click
from click.core import Command, Context

from dagos.components.scanning import component_scanner
from dagos.platform.exceptions import UnsupportedPlatformException


class ManageCLI(click.MultiCommand):
    def list_commands(self, ctx: Context) -> t.List[str]:
        logging.trace("Listing 'manage' commands")
        ctx.obj = component_scanner.find_components()
        commands = []
        for name in sorted(ctx.obj):
            cli = ctx.obj[name].cli
            if cli.exists():
                commands.append(name)
        commands.sort()
        return commands

    def get_command(self, ctx: Context, cmd_name: str) -> t.Optional[Command]:
        logging.trace(f"Getting command '{cmd_name}'")
        if ctx.obj is None:
            ctx.obj = component_scanner.find_component(cmd_name)
            component = ctx.obj
        else:
            component = ctx.obj[cmd_name]
        ns = {}
        fn = component.cli
        with open(fn) as f:
            try:
                try:
                    code = compile(f.read(), fn, "exec")
                    eval(code, ns, ns)
                except ModuleNotFoundError as e:
                    if "ansible" in e.msg:
                        raise UnsupportedPlatformException(
                            "Install DAG-OS 'ansible' extras!"
                        )
                    logging.trace(f"Unhandled ModuleNotFoundError!")
                    raise UnsupportedPlatformException(e)
            except UnsupportedPlatformException as e:
                logging.debug(f"Disabling '{cmd_name}' software component: {e}")
                return None
        return ns["cli"]


@click.command(cls=ManageCLI)
def manage():
    """
    Manage software components.
    """
    pass
