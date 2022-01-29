import shutil

from pytest_bdd import parsers, then


@then(parsers.parse('"{command}" should be installed'), target_fixture="command")
def dagos_should_install_my_software_component(command):
    """DAG-OS should install my software component."""
    assert shutil.which(command) != None
