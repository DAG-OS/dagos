from pathlib import Path

from dagos.core.environments import SoftwareEnvironment
from dagos.core.environments import SoftwareEnvironmentRegistry


def test_constructor_with_basic_env(test_data_dir: Path):
    file = test_data_dir.joinpath("environments/basic.yml")

    result = SoftwareEnvironment(file)

    assert result.name == "basic"
    assert result.description != None
    assert result.platform.os == ["linux"]
    assert len(result.platform.images) == 2
    assert result.platform.images[0].id == "rockylinux"
    assert result.platform.images[0].package_manager == "dnf"
    assert result.platform.images[0].packages == ["git", "python38", "python38-pip"]
    assert len(result.components) == 1
    assert result.components[0].name == "vale"
    assert result.components[0].purpose == "Lint some documents."

    assert SoftwareEnvironmentRegistry.find_environment("basic") == result
