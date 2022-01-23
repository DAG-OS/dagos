"""Using custom software components feature tests."""

from pytest_bdd import given, parsers, scenario, then, when


@scenario(
    "custom_components.feature", "Adding a custom software component to the DAG-OS CLI"
)
def test_adding_a_custom_software_component_to_the_dagos_cli():
    """Adding a custom software component to the DAG-OS CLI."""
    pass


@given(
    parsers.parse('I have a custom software component called "{component:s}"'),
    target_fixture="component",
)
def i_have_a_custom_software_component_called_test(component_name):
    """I have a custom software component called "test"."""
    print(component_name)
    return component_name


@when("I store it in the search path")
def i_store_it_in_the_search_path(component):
    """I store it in the search path."""
    raise NotImplementedError


@when('call "dagos manage test --help"')
def call_dagos_manage_test_help():
    """call "dagos manage test --help"."""
    raise NotImplementedError


@then('I should see the "test" help message')
def i_should_see_the_test_help_message():
    """I should see the "test" help message."""
    raise NotImplementedError
