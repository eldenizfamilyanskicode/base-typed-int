from __future__ import annotations

from typing import TypeVar

from base_typed_int import BaseTypedInt

BaseTypedIntSubtype = TypeVar(
    "BaseTypedIntSubtype",
    bound=BaseTypedInt,
)


def assert_exact_typed_int_instance(
    value: object,
    *,
    expected_plain_value: int,
    expected_type: type[BaseTypedIntSubtype],
) -> None:
    assert value == expected_plain_value
    assert isinstance(value, expected_type)
    assert isinstance(value, BaseTypedInt)
    assert isinstance(value, int)
    assert not isinstance(value, bool)
    assert type(value) is expected_type
