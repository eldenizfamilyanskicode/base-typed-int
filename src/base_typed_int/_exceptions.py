class BaseTypedIntError(Exception):
    """Root exception for all base_typed_int errors."""


class BaseTypedIntInvalidInputValueError(BaseTypedIntError, TypeError):
    """Raised when a non-integer input value is provided."""


class BaseTypedIntInvariantViolationError(BaseTypedIntError):
    """Raised when an internal invariant or contract is violated."""
