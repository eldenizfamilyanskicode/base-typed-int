from __future__ import annotations

from base_typed_int import (
    BaseConstrainedTypedInt,
    BaseTypedIntConstraintViolationError,
)


class RequestExecutionLeaseTtlMilliseconds(BaseConstrainedTypedInt):
    ge = 1_000
    le = 3_600_000


def is_runtime_integer(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def main() -> None:
    lease_ttl = RequestExecutionLeaseTtlMilliseconds(30_000)

    print(f"value: {lease_ttl}")
    print(f"runtime type: {type(lease_ttl).__name__}")
    print(f"is real int: {is_runtime_integer(lease_ttl)}")

    try:
        RequestExecutionLeaseTtlMilliseconds(500)
    except BaseTypedIntConstraintViolationError as constraint_error:
        print(f"rejected: {constraint_error}")


if __name__ == "__main__":
    main()
