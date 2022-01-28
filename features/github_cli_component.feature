@integration
Feature: Manage the GitHub CLI

Scenario: Install the GitHub CLI
    Given DAG-OS CLI is installed
    And I have root privileges
    When I call "dagos manage github_cli install"
    Then GitHub CLI should be installed

# TODO: Scenario currently does not work because GitHub CLI requires authentication
# for everything, even though this partiucular use case should not require it.
# See: https://github.com/cli/cli/issues/2680
Scenario: Installing custom software component via GitHub CLI
    Given I have following YAML:
        ---
        name: "vale"
        action: "install"
        via: "github_cli"
        repository: "https://github.com/errata-ai/vale"
        pattern: "vale*Linux_64*.tar.gz"
        install_dir: "/opt/vale"
    And I have root privileges

    When I store this YAML at "/opt/dagos/components/vale/install.yml"
    And call "dagos -vv manage vale install"
    #OR call "dagos install vale"?

    Then Vale should be installed
