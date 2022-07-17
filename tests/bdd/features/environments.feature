Feature: Manage software environments

    @integration
    Scenario: Deploy a software environment locally
        Given I have a file "environments/basic.yml"
        And I have root privileges

        When I store this file at "~/.dagos/environments/basic.yml"
        # TODO: Scan for environments and provide as options in CLI
        And run "dagos -v env deploy ~/.dagos/environments/basic.yml"

        Then I see "Deploying environment 'basic'"
        And "vale" is installed

    @container
    Scenario: Deploy a software environment into a container
        Given I have a file "environments/basic.yml"

        When I store this file at "~/.dagos/environments/basic.yml"
        And run "dagos -v env deploy --container ~/.dagos/environments/basic.yml"

        Then I see "Deploying environment 'basic' into 'rockylinux' container image"
        And I see "Committed image 'basic'"

        Then I start container from "basic"
        And "vale" is installed in container
