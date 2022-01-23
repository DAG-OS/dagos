Feature: Using custom software components

Scenario: Adding a custom software component to the DAG-OS CLI
    Given I have a custom software component called "test"

    When I store it in the search path
    And call "dagos manage test --help"

    Then I should see the "test" help message

#Scenario: Create custom software component
#Scenario: Configure custom software component
