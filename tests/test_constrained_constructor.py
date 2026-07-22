from __future__ import annotations

import json
from typing import Any

import pytest

from base_typed_int import (
    BaseConstrainedTypedInt,
    BaseTypedInt,
    BaseTypedIntConstraintViolationError,
    BaseTypedIntError,
    BaseTypedIntInvalidInputValueError,
)
from tests.testing_assertions import assert_exact_typed_int_instance


class PositiveInt(BaseConstrainedTypedInt):
    gt = 0


class NonNegativeInt(BaseConstrainedTypedInt):
    ge = 0


class LessThanTenInt(BaseConstrainedTypedInt):
    lt = 10


class AtMostTenInt(BaseConstrainedTypedInt):
    le = 10


class EvenInt(BaseConstrainedTypedInt):
    multiple_of = 2


class EmptyConstraintIntermediateInt(BaseConstrainedTypedInt):
    pass


class MisleadingSourceInt(BaseTypedInt):
    def __int__(self) -> int:
        return 2


class MisleadingConstrainedInt(BaseConstrainedTypedInt):
    multiple_of = 2

    def __int__(self) -> int:
        return 2


class PrivateHelperNameCollisionInt(BaseConstrainedTypedInt):
    ge = 2

    @classmethod
    def _validate_value_constraints(cls, **kwargs: Any) -> None:
        del cls
        del kwargs


def test_valid_value_preserves_exact_constrained_subtype() -> None:
    constrained_value: PositiveInt = PositiveInt(1)

    assert_exact_typed_int_instance(
        constrained_value,
        expected_plain_value=1,
        expected_type=PositiveInt,
    )
    assert isinstance(constrained_value, BaseConstrainedTypedInt)


def test_base_constrained_typed_int_can_be_instantiated_directly() -> None:
    constrained_value = BaseConstrainedTypedInt(42)

    assert_exact_typed_int_instance(
        constrained_value,
        expected_plain_value=42,
        expected_type=BaseConstrainedTypedInt,
    )


def test_subclass_without_constraints_has_explicit_no_op_behavior() -> None:
    constrained_value = EmptyConstraintIntermediateInt(-42)

    assert_exact_typed_int_instance(
        constrained_value,
        expected_plain_value=-42,
        expected_type=EmptyConstraintIntermediateInt,
    )


@pytest.mark.parametrize(
    ("constrained_type", "valid_value"),
    [
        (PositiveInt, 1),
        (NonNegativeInt, 0),
        (LessThanTenInt, 9),
        (AtMostTenInt, 10),
        (EvenInt, -2),
        (EvenInt, 0),
    ],
)
def test_constraint_boundaries_accept_valid_values(
    constrained_type: type[BaseConstrainedTypedInt],
    valid_value: int,
) -> None:
    assert constrained_type(valid_value) == valid_value


@pytest.mark.parametrize(
    ("constrained_type", "invalid_value", "constraint_message"),
    [
        (PositiveInt, 0, "gt=0"),
        (NonNegativeInt, -1, "ge=0"),
        (LessThanTenInt, 10, "lt=10"),
        (AtMostTenInt, 11, "le=10"),
        (EvenInt, 3, "multiple_of=2"),
    ],
)
def test_constraint_violation_raises_explicit_error(
    constrained_type: type[BaseConstrainedTypedInt],
    invalid_value: int,
    constraint_message: str,
) -> None:
    with pytest.raises(BaseTypedIntConstraintViolationError) as caught_error:
        constrained_type(invalid_value)

    assert str(caught_error.value) == (
        f"{constrained_type.__name__} value violates {constraint_message}."
    )


def test_constraint_violation_is_package_error_and_value_error() -> None:
    with pytest.raises(BaseTypedIntConstraintViolationError) as caught_error:
        PositiveInt(0)

    assert isinstance(caught_error.value, BaseTypedIntError)
    assert isinstance(caught_error.value, ValueError)


def test_constraint_error_does_not_expose_input_value() -> None:
    secret_invalid_value = 837_492

    with pytest.raises(BaseTypedIntConstraintViolationError) as caught_error:
        LessThanTenInt(secret_invalid_value)

    assert str(secret_invalid_value) not in str(caught_error.value)


def test_constructor_accepts_existing_base_typed_int() -> None:
    source_value = BaseTypedInt(2)

    constrained_value = EvenInt(source_value)

    assert_exact_typed_int_instance(
        constrained_value,
        expected_plain_value=2,
        expected_type=EvenInt,
    )


def test_constructor_ignores_source_integer_subclass_int_override() -> None:
    source_value = MisleadingSourceInt(3)

    with pytest.raises(BaseTypedIntConstraintViolationError):
        EvenInt(source_value)


def test_constructor_accepts_existing_constrained_typed_int() -> None:
    source_value = EvenInt(2)

    copied_value = EvenInt(source_value)

    assert copied_value == source_value
    assert copied_value is not source_value
    assert type(copied_value) is EvenInt


@pytest.mark.parametrize("invalid_value", [True, False, 1.0, "1", None])
def test_non_integer_input_uses_existing_invalid_input_error(
    invalid_value: Any,
) -> None:
    with pytest.raises(BaseTypedIntInvalidInputValueError):
        PositiveInt(invalid_value)


def test_overridden_int_cannot_spoof_constraint_validation() -> None:
    with pytest.raises(BaseTypedIntConstraintViolationError):
        MisleadingConstrainedInt(3)


def test_private_helper_name_collision_cannot_bypass_validation() -> None:
    with pytest.raises(BaseTypedIntConstraintViolationError):
        PrivateHelperNameCollisionInt(1)


def test_normal_integer_operations_return_plain_int_without_revalidation() -> None:
    constrained_value = PositiveInt(1)

    decremented_value = constrained_value - 2

    assert decremented_value == -1
    assert type(decremented_value) is int


def test_repr_uses_exact_constrained_subtype_name_and_stored_value() -> None:
    constrained_value = MisleadingConstrainedInt(4)

    assert repr(constrained_value) == "MisleadingConstrainedInt(4)"


def test_hash_and_equality_match_plain_integer() -> None:
    constrained_value = PositiveInt(1)

    assert constrained_value == 1
    assert hash(constrained_value) == hash(1)


def test_json_roundtrip_uses_plain_integer_boundary() -> None:
    constrained_value = PositiveInt(1)

    serialized_value = json.dumps(constrained_value)
    restored_value = json.loads(serialized_value)

    assert serialized_value == "1"
    assert restored_value == 1
    assert type(restored_value) is int
