@integration
Feature: Manage common software components

    Scenario Outline: Install common software components via manage
        Given I have root privileges
        When I run "dagos -vv manage <component> install"
        Then "<command>" is installed

        Examples:
            | component   | command     |
            | github-cli  | gh          |
            | structurizr | structurizr |

    Scenario Outline: Install common software components via install
        Given I have root privileges
        When I run "dagos -vv install <component>"
        Then "<command>" is installed

        Examples:
            | component | command |
            | vale      | vale    |
            | miniconda | conda   |
            | poetry    | poetry  |

    Scenario: Install SDKMAN
        When I run "dagos -vv install sdkman"
        # TODO: Why is the .sdkman folder not under the root home dir?
        #   Only happens in test? Probably an issue with the test image.
        And I run "bash -c 'source /.sdkman/bin/sdkman-init.sh; sdk version'"
        Then I see "SDKMAN "
