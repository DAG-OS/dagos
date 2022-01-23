from pytest_bdd import given, scenario, then, when


@scenario("system_packages.feature", "Install system packages from a file")
def test_install_packages_from_file():
    pass


@given("I have a file with a list of system packages")
def read_file_list():
    # Add Your Code Here
    pass


@when("I use dagos to install them")
def install_system_packages():
    pass


@then("all packages are installed")
def check_installation():
    pass
