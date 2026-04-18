from __future__ import annotations

from typing import Any

import pytest

from base_typed_int import BaseTypedInt, BaseTypedIntInvalidInputValueError
from tests.testing_assertions import assert_exact_typed_int_instance
from tests.testing_types import AdminUserAge, UserAge


def test_zero_is_valid() -> None:
    typed_value: UserAge = UserAge(0)

    assert_exact_typed_int_instance(
        typed_value,
        expected_plain_value=0,
        expected_type=UserAge,
    )


def test_negative_integer_is_valid() -> None:
    typed_value: UserAge = UserAge(-7)

    assert_exact_typed_int_instance(
        typed_value,
        expected_plain_value=-7,
        expected_type=UserAge,
    )


def test_second_level_subclass_instantiation_preserves_exact_runtime_type() -> None:
    typed_value: AdminUserAge = AdminUserAge(99)

    assert_exact_typed_int_instance(
        typed_value,
        expected_plain_value=99,
        expected_type=AdminUserAge,
    )

    assert isinstance(typed_value, UserAge)


def test_base_typed_int_can_be_instantiated_directly() -> None:
    typed_value: BaseTypedInt = BaseTypedInt(42)

    assert_exact_typed_int_instance(
        typed_value,
        expected_plain_value=42,
        expected_type=BaseTypedInt,
    )


def test_subclass_instantiation_preserves_exact_runtime_type() -> None:
    typed_value: UserAge = UserAge(18)

    assert_exact_typed_int_instance(
        typed_value,
        expected_plain_value=18,
        expected_type=UserAge,
    )


def test_constructor_accepts_existing_typed_int_instance() -> None:
    source_value: UserAge = UserAge(21)

    copied_value: UserAge = UserAge(source_value)

    assert_exact_typed_int_instance(
        copied_value,
        expected_plain_value=21,
        expected_type=UserAge,
    )


@pytest.mark.parametrize(
    ("invalid_value", "expected_type_name", "expected_message_part"),
    [
        ("123", "str", "BaseTypedInt must be initialized only with int"),
        (None, "NoneType", "BaseTypedInt must be initialized only with int"),
        (True, "bool", "bool is not allowed"),
        (3.14, "float", "BaseTypedInt must be initialized only with int"),
        (object(), "object", "BaseTypedInt must be initialized only with int"),
    ],
)
def test_non_integer_input_raises_domain_error(
    invalid_value: Any,
    expected_type_name: str,
    expected_message_part: str,
) -> None:
    with pytest.raises(BaseTypedIntInvalidInputValueError) as caught_error:
        UserAge(invalid_value)

    error_message: str = str(caught_error.value)

    assert expected_message_part in error_message
    assert expected_type_name in error_message
