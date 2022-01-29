@integration
Feature: Manage software components via actions

    Scenario Outline: Install custom software components via actions
        Given I have a file "actions/<component>-install.yml"
        And I have root privileges

        When I store this file at "/opt/dagos/components/<component>/install.yml"
        And run "dagos -v manage <component> install"
        #OR run "dagos install <component>"

        Then "<component>" is installed

        Examples:
            | component  |
            | bat        |
            | shellcheck |
