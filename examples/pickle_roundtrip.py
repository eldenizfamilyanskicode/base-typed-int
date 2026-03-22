from __future__ import annotations

import pickle

from base_typed_int import BaseTypedInt


class RetryCount(BaseTypedInt):
    pass


def print_section(title: str) -> None:
    separator: str = "=" * len(title)
    print()
    print(separator)
    print(title)
    print(separator)


def print_value_state(label: str, value: object) -> None:
    print(f"{label}:")
    print(f"  repr         : {value!r}")
    print(f"  runtime type : {type(value).__name__}")
    print()


def main() -> None:
    print_section("pickle roundtrip preserves exact subtype")

    source_retry_count: RetryCount = RetryCount(7)
    serialized_retry_count: bytes = pickle.dumps(source_retry_count)
    restored_retry_count: object = pickle.loads(serialized_retry_count)

    print_value_state("source_retry_count", source_retry_count)
    print_value_state("restored_retry_count", restored_retry_count)

    print(f"plain value preserved            : {restored_retry_count == 7}")
    print(f"exact subtype preserved          : {type(restored_retry_count) is RetryCount}")
    print(f"isinstance(restored_retry_count, int): {isinstance(restored_retry_count, int)}")
    print(
        f"isinstance(restored_retry_count, RetryCount): "
        f"{isinstance(restored_retry_count, RetryCount)}"
    )
    print(f"serialized byte length           : {len(serialized_retry_count)}")


if __name__ == "__main__":
    main()