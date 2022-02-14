@integration
Feature: Manage common software components

    Scenario Outline: Install common software components via manage
        Given I have root privileges
        When I run "dagos -v manage <component> install"
        Then "<command>" is installed

        Examples:
            | component   | command         |
            | github-cli  | gh              |
            | structurizr | structurizr-cli |

    Scenario Outline: Install common software components via install
        Given I have root privileges
        When I run "dagos -v install <component>"
        Then "<command>" is installed

        Examples:
            | component   | command         |
            | vale        | vale            |
