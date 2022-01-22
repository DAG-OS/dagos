class MissingDependenciesException(Exception):
    """Required dependencies for a software component are missing."""


class ConfigurationException(Exception):
    """An exception occured while configuring a software component."""
