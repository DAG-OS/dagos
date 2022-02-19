Feature: Configure DAG-OS CLI

    DAG-OS, its software components and environments require configuration.
    Providing all of it via the CLI is cumbersome and error-prone. It must be
    possible to add configuration via one or multiple files. Especially when
    project- or user-specifics are involved.

    Scenario: Configure the CLIs' default verbosity level
        Given I have following text:
            verbosity: 1

        When I store this text at "~/.dagos/config.yml"
        And run "dagos manage"

        Then I see no "TRACE" messages
