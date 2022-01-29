@integration
Feature: Manage common software components

    Scenario Outline: Install common software components
        Given I have root privileges
        When I run "dagos -v manage <component> install"
        Then "<command>" is installed

        Examples:
            | component   | command         |
            | vale        | vale            |
            | github_cli  | gh              |
            | structurizr | structurizr-cli |
