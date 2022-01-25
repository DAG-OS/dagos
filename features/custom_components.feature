@integration
Feature: Using custom software components

Scenario: Adding a minimal software component
    Given I have following YAML:
        name: "vale"
        action: "install"
        via: "github"
        repository: "https://github.com/errata-ai/vale"
        pattern: "vale*Linux_64*.tar.gz"

    When I store this YAML at "/opt/dagos/components/vale/install.yml"
    And call "dagos -vv manage vale install"
    #OR call "dagos install vale"?

    Then Vale should be installed
