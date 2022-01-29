Feature: Manage generic system packages

Scenario: Install system packages from a file
    Given I have a file with a list of system packages

    When I use dagos to install them

    Then all packages are installed
