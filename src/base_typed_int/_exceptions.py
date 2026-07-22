class BaseTypedIntError(Exception):
    """Root exception for all base_typed_int errors."""


class BaseTypedIntConstraintConfigurationError(BaseTypedIntError, ValueError):
    """Raised when typed integer constraints are configured incorrectly."""


class BaseTypedIntConstraintViolationError(BaseTypedIntError, ValueError):
    """Raised when an integer value violates its declared constraints."""


class BaseTypedIntInvalidInputValueError(BaseTypedIntError, TypeError):
    """Raised when a non-integer input value is provided."""


class BaseTypedIntInvariantViolationError(BaseTypedIntError):
    """Raised when an internal invariant or contract is violated."""
