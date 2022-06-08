Feature: List software components and environments

    As a mean to gather information and debug available software components and
    environments the CLI shall provide a command to list all found components
    and environments.

    Scenario: List software components
        When I run "dagos list --components"
        Then I see "Software Components \(\d+\)"
        Then I do not see "Software Environments \(\d+\)"

    Scenario: List software environments
        When I run "dagos list --environments"
        Then I see "Software Environments \(\d+\)"
        Then I do not see "Software Components \(\d+\)"

    Scenario: List both software components and software environments
        When I run "dagos list"
        Then I see "Software Components \(\d+\)"
        Then I see "Software Environments \(\d+\)"
