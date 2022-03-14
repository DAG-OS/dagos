@container
Feature: Manage WSL distros and instances

    Scenario: Prepare WSL distro from image
        When I run "dagos -v wsl prepare --image busybox"
        Then "busybox.tar" is created
        Then I delete "busybox.tar"

    Scenario: Prepare WSL distro from container
        Given I have a running container named "busybox"
        When I run "dagos -v wsl prepare --container busybox"
        Then "docker.io_library_busybox_latest.tar" is created
        And I delete "docker.io_library_busybox_latest.tar"
