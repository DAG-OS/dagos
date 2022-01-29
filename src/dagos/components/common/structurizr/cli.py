import click

from dagos.components.domain import SoftwareComponent


@click.group(name="structurizr")
def cli():
    """
    Manage Structurizr CLI.

    Project home: https://github.com/structurizr/cli
    """
    pass


@cli.command()
@click.pass_context
def install(ctx: click.Context):
    """Install Structurzir CLI."""
    # TODO: Allow combining CLI with actions
    component: SoftwareComponent = ctx.obj
    component.actions[0].execute_action()
    # TODO: Make structurizr CLI executable and put it on the path
