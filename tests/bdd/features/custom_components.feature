@integration
Feature: Manage custom software components

    Scenario: Add custom component to CLI
        Given I have a folder "components/idea/"
        And I have root privileges

        When I store this folder at "/root/.dagos/components/idea/"
        And run "dagos manage idea"

        Then I see "Manage the IntelliJ IDE."
        And I see a command "install" with the description "Install the IntelliJ IDE."
        And I see a command "uninstall" with the description "Uninstall the idea software component."

    Scenario Outline: Install custom software components via actions
        Given I have a file "actions/<component>-install.yml"
        And I have root privileges

        When I store this file at "/opt/dagos/components/<component>/install.yml"
        And run "dagos install <component>"

        Then "<component>" is installed

        Examples:
            | component  |
            | bat        |
            | shellcheck |
