from pathlib import Path

from pytest_bdd import scenarios

features_base_dir = str(Path(__file__).parent / "features")

scenarios("configure_dagos.feature", features_base_dir=features_base_dir)
scenarios("common_components.feature", features_base_dir=features_base_dir)
scenarios("custom_components.feature", features_base_dir=features_base_dir)
scenarios("environments.feature", features_base_dir=features_base_dir)
scenarios("wsl.feature", features_base_dir=features_base_dir)
