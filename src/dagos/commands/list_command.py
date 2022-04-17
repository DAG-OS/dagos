import click
from rich.text import Text

from dagos.core.components import SoftwareComponentRegistry
from dagos.core.environments import SoftwareEnvironmentRegistry
from dagos.logging import console


@click.command()
@click.option(
    "--components",
    is_flag=True,
    default=False,
    help="Control if components should be listed.",
)
@click.option(
    "--environments",
    is_flag=True,
    default=False,
    help="Control if environments should be listed.",
)
def list(components: bool, environments: bool):
    """List available components and/or environments.

    If neither --components nor --environments is provided both are listed.
    """
    if not components and not environments:
        components, environments = True, True
    if components:
        component_amount = len(SoftwareComponentRegistry.components)
        console.print(render_title(f"Software Components ({component_amount})"))
        for component in SoftwareComponentRegistry.components:
            console.print(component)
    if environments:
        env_amount = len(SoftwareEnvironmentRegistry.environments)
        console.print(render_title(f"Software Environments ({env_amount})"))
        for environment in SoftwareEnvironmentRegistry.environments:
            console.print(environment)


def render_title(title: str) -> Text:
    return Text(text=title, style="table.title")
