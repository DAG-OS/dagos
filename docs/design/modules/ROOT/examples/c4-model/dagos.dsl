workspace {

    !identifiers hierarchical

    !constant CLICK_COMMAND "Click Command"

    model {
        user = person "Environment User"
        creator = person "Environment Creator"

        enterprise DAG-OS {
            dagos = softwareSystem "DAG-OS" "A tool for managing software components and environments" {
                cli = container "Command Line Interface" "Provide an interface for managing software components and environments" "Python" {
                    group "CLI commands" {
                        wsl = component "wsl" "Configure WSL instances or import prepared software environments as a WSL distro" "${CLICK_COMMAND}"
                        manage = component "manage" "Manage a dynamic set of software components, such as Git, LaTeX, or Zsh" "${CLICK_COMMAND}"
                    }
                    scanner = component "Component Scanner" "Scan the system for software components" "Python Module"
                }
            }
        }

        containers = softwareSystem "Container Engine" "OCI-compliant container engine, such as Docker or Podman" {
            docker = container "Docker"
            podman = container "Podman"
        }

        fs = softwareSystem "File System" "The local file system"

        ansible = softwareSystem "Ansible" "Radically simple IT automation"
        bash = softwareSystem "Bash" "An sh-compatible command language interpreter"
        powershell = softwareSystem "PowerShell" "A cross-platform task automation solution"
        wsl = softwareSystem "WSL" "A GNU/Linux environment run directly on Windows"

        # TODO: Create environments which can be turned into WSL distros
        creator -> dagos.cli.wsl "Prepare WSL distros"

        user -> dagos.cli.wsl "Import prepared WSL distros"
        user -> dagos.cli.manage "Manage individual software components"

        dagos.cli.wsl -> containers.podman "Export containers or images"
        dagos.cli.wsl -> containers.docker "Export containers or images"
        dagos.cli.wsl -> wsl "Configure instances or import distros"

        dagos.cli.manage -> dagos.cli.scanner "Find available software components"

        dagos.cli.scanner -> ansible "Wrap installed roles"
        dagos.cli.scanner -> fs "Scan for software components and environments"
    }

    views {
        systemContext dagos {
            include *
            autoLayout
        }

        container dagos {
            include *
            autoLayout
        }

        component dagos.cli {
            include *
            autoLayout
        }
    }
}
