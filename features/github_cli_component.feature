@integration
Feature: Manage the GitHub CLI

Scenario: Install the GitHub CLI
    Given DAG-OS CLI is installed
    And I have root privileges
    When I call "dagos manage github_cli install"
    Then "gh" should be installed

Scenario: Installing custom software component via GitHub CLI
    Given I have following YAML:
        ---
        name: "bat"
        action: "install"
        via: "github_cli"
        repository: "sharkdp/bat"
        pattern: "bat-*-x86_64-unknown-linux-gnu.tar.gz"
        install_dir: "/opt/bat"
        strip_root_folder: true
        binary: bat
    And I have root privileges

    When I store this YAML at "/opt/dagos/components/bat/install.yml"
    And call "dagos -vv manage bat install"
    #OR call "dagos install bat"?

    Then "bat" should be installed
