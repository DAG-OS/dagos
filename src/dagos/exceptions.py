class DagosException(Exception):
    """A base class for all DAG-OS related exceptions."""


class SoftwareComponentScanException(DagosException):
    """A base exception for all component scanning errors."""
