from __future__ import annotations

from abc import ABC, ABCMeta
from typing import Any

import pytest

from base_typed_int import (
    BaseConstrainedTypedInt,
    BaseTypedIntConstraintConfigurationError,
    BaseTypedIntError,
    BaseTypedIntInvariantViolationError,
)


def _create_constrained_type(
    class_name: str,
    class_attributes: dict[str, Any],
    *,
    parent_type: type[BaseConstrainedTypedInt] = BaseConstrainedTypedInt,
) -> type[BaseConstrainedTypedInt]:
    return type(class_name, (parent_type,), class_attributes)


class ABCCompatibleConstrainedInt(BaseConstrainedTypedInt, ABC):
    ge = 1


class DomainMeta(type):
    pass


class DomainMixin(metaclass=DomainMeta):
    pass


class CustomMetaclassConstrainedInt(BaseConstrainedTypedInt, DomainMixin):
    ge = 1


def test_constrained_type_is_compatible_with_abc_meta() -> None:
    constrained_value = ABCCompatibleConstrainedInt(1)

    assert type(ABCCompatibleConstrainedInt) is ABCMeta
    assert type(constrained_value) is ABCCompatibleConstrainedInt


def test_constrained_type_is_compatible_with_independent_metaclass() -> None:
    constrained_value = CustomMetaclassConstrainedInt(1)

    assert type(CustomMetaclassConstrainedInt) is DomainMeta
    assert type(constrained_value) is CustomMetaclassConstrainedInt


@pytest.mark.parametrize(
    ("constraint_name", "invalid_value", "invalid_type_name"),
    [
        ("gt", True, "bool"),
        ("gt", 1.5, "float"),
        ("ge", "1", "str"),
        ("lt", False, "bool"),
        ("le", object(), "object"),
        ("multiple_of", 1.5, "float"),
    ],
)
def test_non_integer_constraint_configuration_is_rejected(
    constraint_name: str,
    invalid_value: object,
    invalid_type_name: str,
) -> None:
    with pytest.raises(BaseTypedIntConstraintConfigurationError) as caught_error:
        _create_constrained_type(
            "InvalidConstraintType",
            {constraint_name: invalid_value},
        )

    assert str(caught_error.value) == (
        f"InvalidConstraintType.{constraint_name} must be int or None. "
        f"Got: {invalid_type_name}."
    )


@pytest.mark.parametrize("invalid_multiple", [0, -1])
def test_non_positive_multiple_of_is_rejected(invalid_multiple: int) -> None:
    with pytest.raises(BaseTypedIntConstraintConfigurationError) as caught_error:
        _create_constrained_type(
            "InvalidMultiple",
            {"multiple_of": invalid_multiple},
        )

    assert str(caught_error.value) == (
        "InvalidMultiple.multiple_of must be greater than zero. "
        f"Got: {invalid_multiple}."
    )


def test_negative_bounds_are_valid_configuration() -> None:
    negative_range_type = _create_constrained_type(
        "NegativeRange",
        {"ge": -5, "le": -1},
    )

    assert negative_range_type(-3) == -3


@pytest.mark.parametrize(
    "class_attributes",
    [
        {"ge": 2, "le": 1},
        {"gt": 1, "lt": 2},
        {"ge": 1, "le": 2, "multiple_of": 3},
    ],
)
def test_configuration_without_any_permitted_integer_is_rejected(
    class_attributes: dict[str, int],
) -> None:
    with pytest.raises(BaseTypedIntConstraintConfigurationError) as caught_error:
        _create_constrained_type("EmptyIntegerDomain", class_attributes)

    assert str(caught_error.value) == (
        "EmptyIntegerDomain constraints do not permit any integer value."
    )


def test_single_permitted_integer_is_valid_configuration() -> None:
    exact_value_type = _create_constrained_type(
        "ExactValue",
        {"gt": 1, "lt": 3, "multiple_of": 2},
    )

    assert exact_value_type(2) == 2


def test_constraint_configuration_error_is_package_error_and_value_error() -> None:
    with pytest.raises(BaseTypedIntConstraintConfigurationError) as caught_error:
        _create_constrained_type("InvalidMultiple", {"multiple_of": 0})

    assert isinstance(caught_error.value, BaseTypedIntError)
    assert isinstance(caught_error.value, ValueError)


class ParentConstrainedInt(BaseConstrainedTypedInt):
    ge = 0
    le = 100
    multiple_of = 2


class NarrowerChildConstrainedInt(ParentConstrainedInt):
    gt = 0
    lt = 100
    multiple_of = 4


class SameConstraintGrandchild(NarrowerChildConstrainedInt):
    pass


class SealedParentConstrainedInt(BaseConstrainedTypedInt):
    ge = 1


class SealedChildConstrainedInt(SealedParentConstrainedInt):
    pass


class EvenConstrainedInt(BaseConstrainedTypedInt):
    multiple_of = 2


class DivisibleByThreeConstrainedInt(BaseConstrainedTypedInt):
    multiple_of = 3


class DivisibleBySixConstrainedInt(BaseConstrainedTypedInt):
    multiple_of = 6


def test_child_can_tighten_inherited_constraints() -> None:
    constrained_value = NarrowerChildConstrainedInt(4)

    assert constrained_value == 4
    assert type(constrained_value) is NarrowerChildConstrainedInt
    assert NarrowerChildConstrainedInt.ge == 0
    assert NarrowerChildConstrainedInt.gt == 0
    assert NarrowerChildConstrainedInt.le == 100
    assert NarrowerChildConstrainedInt.lt == 100
    assert NarrowerChildConstrainedInt.multiple_of == 4


def test_child_can_express_an_equivalent_bound_in_another_form() -> None:
    equivalent_lower_bound_child = _create_constrained_type(
        "EquivalentLowerBoundChild",
        {"ge": None, "gt": -1},
        parent_type=ParentConstrainedInt,
    )

    assert equivalent_lower_bound_child(2) == 2
    assert equivalent_lower_bound_child.ge is None
    assert equivalent_lower_bound_child.gt == -1


@pytest.mark.parametrize(
    "class_attributes",
    [
        {"ge": -1},
        {"ge": None},
        {"le": 101},
        {"le": None},
    ],
)
def test_child_cannot_weaken_inherited_range(
    class_attributes: dict[str, int | None],
) -> None:
    with pytest.raises(BaseTypedIntConstraintConfigurationError):
        _create_constrained_type(
            "WeakerRange",
            class_attributes,
            parent_type=ParentConstrainedInt,
        )


@pytest.mark.parametrize("replacement_multiple", [None, 3])
def test_child_cannot_weaken_inherited_multiple_of(
    replacement_multiple: int | None,
) -> None:
    with pytest.raises(BaseTypedIntConstraintConfigurationError) as caught_error:
        _create_constrained_type(
            "WeakerMultiple",
            {"multiple_of": replacement_multiple},
            parent_type=ParentConstrainedInt,
        )

    assert "multiple_of cannot weaken inherited multiple_of=2" in str(
        caught_error.value
    )


def test_grandchild_inherits_constraints_and_preserves_exact_type() -> None:
    constrained_value = SameConstraintGrandchild(4)

    assert constrained_value == 4
    assert type(constrained_value) is SameConstraintGrandchild
    assert isinstance(constrained_value, NarrowerChildConstrainedInt)


def test_changed_parent_constraint_is_rejected_when_child_is_used() -> None:
    SealedParentConstrainedInt.ge = 2
    try:
        with pytest.raises(BaseTypedIntConstraintConfigurationError) as caught_error:
            SealedChildConstrainedInt(2)
    finally:
        SealedParentConstrainedInt.ge = 1

    assert str(caught_error.value) == (
        "SealedParentConstrainedInt.ge cannot be changed after class creation. "
        "Declare constraints in the class body."
    )


def test_multiple_constrained_integer_inheritance_is_rejected() -> None:
    try:
        type(
            "MultiplyInheritedConstrainedInt",
            (EvenConstrainedInt, DivisibleByThreeConstrainedInt),
            {},
        )
    except BaseTypedIntConstraintConfigurationError as configuration_error:
        assert str(configuration_error) == (
            "MultiplyInheritedConstrainedInt cannot inherit from multiple "
            "constrained integer types: EvenConstrainedInt, "
            "DivisibleByThreeConstrainedInt. Declare "
            "MultiplyInheritedConstrainedInt directly from "
            "BaseConstrainedTypedInt with its own constraints."
        )
    except TypeError as layout_error:
        assert str(layout_error) == "multiple bases have instance lay-out conflict"
    else:
        pytest.fail("Multiple constrained integer inheritance was accepted.")


def test_combined_constraints_are_declared_as_an_independent_type() -> None:
    constrained_value = DivisibleBySixConstrainedInt(6)

    assert type(constrained_value) is DivisibleBySixConstrainedInt
    assert not issubclass(DivisibleBySixConstrainedInt, EvenConstrainedInt)
    assert not issubclass(
        DivisibleBySixConstrainedInt,
        DivisibleByThreeConstrainedInt,
    )


@pytest.mark.parametrize(
    ("constraint_name", "changed_value"),
    [
        ("gt", -2),
        ("ge", -1),
        ("lt", 102),
        ("le", 101),
        ("multiple_of", 4),
    ],
)
def test_changed_constraint_is_rejected_on_next_use(
    constraint_name: str,
    changed_value: object,
) -> None:
    constrained_type = _create_constrained_type(
        "ChangedConstraint",
        {
            "gt": -1,
            "ge": 0,
            "lt": 101,
            "le": 100,
            "multiple_of": 2,
        },
    )

    setattr(constrained_type, constraint_name, changed_value)

    with pytest.raises(BaseTypedIntConstraintConfigurationError) as caught_error:
        constrained_type(2)

    assert str(caught_error.value) == (
        f"ChangedConstraint.{constraint_name} cannot be changed after class creation. "
        "Declare constraints in the class body."
    )


def test_deleted_constraint_is_rejected_on_next_use() -> None:
    constrained_type = _create_constrained_type(
        "DeletedConstraint",
        {"ge": 1},
    )

    delattr(constrained_type, "ge")

    with pytest.raises(BaseTypedIntConstraintConfigurationError) as caught_error:
        constrained_type(1)

    assert str(caught_error.value) == (
        "DeletedConstraint.ge cannot be changed after class creation. "
        "Declare constraints in the class body."
    )


def test_non_constraint_class_attributes_remain_mutable() -> None:
    description_attribute_name = "description"
    mutable_type = _create_constrained_type(
        "MutableNonConstraintAttribute",
        {description_attribute_name: "before"},
    )

    setattr(mutable_type, description_attribute_name, "after")
    assert getattr(mutable_type, description_attribute_name) == "after"

    delattr(mutable_type, description_attribute_name)
    assert not hasattr(mutable_type, description_attribute_name)


def test_invalid_internal_constraint_configuration_fails_explicitly() -> None:
    constrained_type = _create_constrained_type(
        "InvalidInternalConfiguration",
        {"ge": 1},
    )
    configuration_attribute_name = "_constraint_configuration"
    original_configuration = getattr(
        constrained_type,
        configuration_attribute_name,
    )

    setattr(constrained_type, configuration_attribute_name, object())
    try:
        with pytest.raises(BaseTypedIntInvariantViolationError) as caught_error:
            constrained_type(1)
    finally:
        setattr(
            constrained_type,
            configuration_attribute_name,
            original_configuration,
        )

    assert str(caught_error.value) == (
        "InvalidInternalConfiguration internal constraint configuration is invalid."
    )
