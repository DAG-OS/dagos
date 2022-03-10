import click

from .deploy import deploy


@click.group(no_args_is_help=True)
def env():
    """
    Manage software environments.
    """
    pass


env.add_command(deploy)
