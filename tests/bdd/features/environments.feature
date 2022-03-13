@integration
Feature: Manage software environments

    Scenario: Deploy a software environment
        Given I have a file "environments/basic.yml"
        And I have root privileges

        When I store this file at "/root/.dagos/environments/basic.yml"
        # TODO: Scan for environments and provide as options in CLI
        And run "dagos env deploy /root/.dagos/environments/basic.yml"

        Then I see "Deploying environment 'basic'"
        And "vale" is installed
