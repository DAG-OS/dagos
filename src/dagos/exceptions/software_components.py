class MissingDependenciesException(Exception):
    """Required dependencies for a software component are missing."""

    pass


class UnsupportedPlatformException(Exception):
    """A software component does not support the current platform."""

    pass


class ConfigurationException(Exception):
    """An exception occured while configuring a software component."""
