import subprocess

from pytest_bdd import given, parsers, scenario, then, when


@scenario("github_cli_component.feature", "Install the GitHub CLI")
def test_install_the_github_cli():
    """Install the GitHub CLI."""


@given("DAG-OS CLI is installed")
def given_dagos_is_installed():
    """DAG-OS CLI is installed."""


@given("I have root priviliges")
def given_i_have_root_privileges():
    """I have root privileges."""


@when(parsers.parse('I call "{dagos_command}"'))
def i_call_dagos_manage_github_install(dagos_command):
    """I call "dagos manage github install"."""
    subprocess.check_call(dagos_command, shell=True)


@then("GitHub CLI should be installed")
def github_cli_should_be_installed():
    """GitHub CLI should be installed."""
    subprocess.check_call(["gh", "--version"])
