from pytest_bdd import given, parsers


@given("DAG-OS CLI is installed")
def given_dagos_is_installed():
    """DAG-OS CLI is installed."""


@given("I have root privileges")
def i_have_root_privileges():
    """I have root privileges."""


@given(parsers.parse("I have following YAML:\n{yaml}"), target_fixture="i_have_yaml")
def i_have_yaml(yaml):
    """I have a YAML based software component"""
    print(yaml)
    return yaml
