import shutil

from pytest_bdd import parsers, then


@then(parsers.parse('"{command}" is installed'))
def command_shoud_be_installed(command):
    assert shutil.which(command) != None
