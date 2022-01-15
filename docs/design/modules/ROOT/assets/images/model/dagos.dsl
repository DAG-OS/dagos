workspace {

    !identifiers hierarchical

    model {
        user = person "Environment User"
        creator = person "Environment Creator"

        enterprise DAG-OS {
            dagos = softwareSystem "DAG-OS" "A tool for managing software environments" {
                cli = container "Command Line Interface" "Provides an interface for managing software components and environments" "Python" {
                    wsl = component "wsl" "Configure WSL instances or import prepared software environments as a WSL distro"
                    manage = component "manage" "Manage a dynamic set of software components, such as Git, LaTeX, or Zsh"
                }
            }

        }
        containers = softwareSystem "Container Engine" "OCI-compliant container engine, such as Docker or Podman" {
            docker = container "Docker"
            podman = container "Podman"
        }

        ansible = softwareSystem "Ansible" "Radically simple IT automation"
        bash = softwareSystem "Bash" "An sh-compatible command language interpreter"
        wsl = softwareSystem "WSL" "A GNU/Linux environment run directly on Windows"

        creator -> dagos "Defines environments"

        user -> dagos "Uses environments"

        dagos.cli.wsl -> containers.podman "Export containers or images"
        dagos.cli.wsl -> containers.docker "Export containers or images"
        dagos.cli.wsl -> wsl "Configure instances or import distros"

        dagos.cli.manage -> ansible "Wrap available roles"
        dagos.cli.manage -> bash "Run scripts"
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
