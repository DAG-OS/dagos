@integration
Feature: Manage the GitHub CLI

Scenario: Install the GitHub CLI
    Given DAG-OS CLI is installed
    And I have root priviliges
    When I call "dagos manage github-cli install"
    Then GitHub CLI should be installed
