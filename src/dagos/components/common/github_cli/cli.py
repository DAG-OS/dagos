import click

import dagos.platform.utils as platform_utils
from dagos.platform.domain import OperatingSystem

platform_utils.assert_operating_system([OperatingSystem.LINUX])


@click.group(name="github-cli")
def cli():
    """
    Manage GitHub CLI.

    The GitHub CLI is useful for interacting with GitHub from the command line.
    DAG-OS may use it for downloading software components hosted there.
    Project home: https://github.com/cli/cli
    """
    pass
