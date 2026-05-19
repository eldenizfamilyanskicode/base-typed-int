from __future__ import annotations

from typing_extensions import assert_type

from base_typed_int import BaseTypedInt


class UserAge(BaseTypedInt):
    pass


def main() -> None:
    source_user_age: UserAge = UserAge(18)

    values_by_exact_user_age: dict[UserAge, str] = {
        source_user_age: "present",
    }
    exact_keys: tuple[UserAge, ...] = tuple(values_by_exact_user_age.keys())
    exact_key: UserAge = exact_keys[0]

    assert_type(exact_keys, tuple[UserAge, ...])
    assert_type(exact_key, UserAge)

    values_by_plain_int: dict[int, str] = {
        source_user_age: "present",
    }
    plain_keys: tuple[int, ...] = tuple(values_by_plain_int.keys())
    plain_key: int = plain_keys[0]

    assert_type(plain_keys, tuple[int, ...])
    assert_type(plain_key, int)

    print(
        "static type checkers preserve UserAge "
        "when the source container is typed exactly"
    )
    print(f"runtime exact key type: {type(exact_key).__name__}")
    print(f"plain int compatibility key value: {plain_key}")


if __name__ == "__main__":
    main()
