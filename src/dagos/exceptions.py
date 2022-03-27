class DagosException(Exception):
    """A base class for all DAG-OS related exceptions."""


class SoftwareComponentScanException(DagosException):
    """A base exception for all component scanning errors."""


class ValidationException(DagosException):
    """A base exception for all validation errors."""


class SchemaValidationException(ValidationException):
    """A base exception for all schema validation errors."""
