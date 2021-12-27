workspace {

    model {
        user = person "Environment User"
        creator = person "Environment Creator"

        enterprise DAGOS {
            dagos = softwareSystem "DAGOS" {
                container "Command Line Interface"
                common = container "Software components" {
                    component "C++"
                    component "Git"
                    component "IDE"
                    component "LaTeX"
                    component "OhMyZsh"
                    component "Zsh"
                }
            }
        }

        ansible = softwareSystem "Ansible"
        bash = softwareSystem "Bash"
        podman = softwareSystem "Podman"
        ps = softwareSystem "PowerShell"

        dagos -> ansible "Uses"
        dagos -> bash "Uses"
        dagos -> podman "Uses"
        dagos -> ps "Uses"

        creator -> dagos "Defines environments"
        user -> dagos "Uses environments"
    }

    views {
        systemContext dagos "Diagram1" {
            include *
            autoLayout
        }

        container dagos {
            include *
            autoLayout
        }

        component common {
            include *
            autoLayout
        }
    }

}
