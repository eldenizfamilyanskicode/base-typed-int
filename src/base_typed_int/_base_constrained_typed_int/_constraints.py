from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from base_typed_int._exceptions import (
    BaseTypedIntConstraintConfigurationError,
    BaseTypedIntConstraintViolationError,
)


@dataclass(frozen=True, slots=True)
class ConstraintConfiguration:
    gt: int | None
    ge: int | None
    lt: int | None
    le: int | None
    multiple_of: int | None


EMPTY_CONSTRAINT_CONFIGURATION = ConstraintConfiguration(
    gt=None,
    ge=None,
    lt=None,
    le=None,
    multiple_of=None,
)


def build_effective_constraint_configuration(
    *,
    class_name: str,
    class_namespace: Mapping[str, object],
    parent_configuration: ConstraintConfiguration,
) -> ConstraintConfiguration:
    gt_value = class_namespace.get(
        "gt",
        parent_configuration.gt,
    )
    ge_value = class_namespace.get(
        "ge",
        parent_configuration.ge,
    )
    lt_value = class_namespace.get(
        "lt",
        parent_configuration.lt,
    )
    le_value = class_namespace.get(
        "le",
        parent_configuration.le,
    )
    multiple_of_value = class_namespace.get(
        "multiple_of",
        parent_configuration.multiple_of,
    )

    configuration = _build_constraint_configuration(
        class_name=class_name,
        gt_value=gt_value,
        ge_value=ge_value,
        lt_value=lt_value,
        le_value=le_value,
        multiple_of_value=multiple_of_value,
    )
    validate_inherited_constraints(
        class_name=class_name,
        configuration=configuration,
        parent_configuration=parent_configuration,
    )
    return configuration


def _build_constraint_configuration(
    *,
    class_name: str,
    gt_value: object,
    ge_value: object,
    lt_value: object,
    le_value: object,
    multiple_of_value: object,
) -> ConstraintConfiguration:
    configuration = ConstraintConfiguration(
        gt=_validated_bound_constraint(
            class_name=class_name,
            constraint_name="gt",
            constraint_value=gt_value,
        ),
        ge=_validated_bound_constraint(
            class_name=class_name,
            constraint_name="ge",
            constraint_value=ge_value,
        ),
        lt=_validated_bound_constraint(
            class_name=class_name,
            constraint_name="lt",
            constraint_value=lt_value,
        ),
        le=_validated_bound_constraint(
            class_name=class_name,
            constraint_name="le",
            constraint_value=le_value,
        ),
        multiple_of=_validated_multiple_of_constraint(
            class_name=class_name,
            constraint_value=multiple_of_value,
        ),
    )
    _validate_constraint_range(class_name=class_name, configuration=configuration)
    return configuration


def validate_constraint_declaration_unchanged(
    *,
    class_name: str,
    configuration: ConstraintConfiguration,
    current_gt: object,
    current_ge: object,
    current_lt: object,
    current_le: object,
    current_multiple_of: object,
) -> None:
    current_values = {
        "gt": current_gt,
        "ge": current_ge,
        "lt": current_lt,
        "le": current_le,
        "multiple_of": current_multiple_of,
    }

    for constraint_name, current_value in current_values.items():
        configured_value = getattr(configuration, constraint_name)
        if not _integer_declaration_matches(
            current_value=current_value,
            configured_value=configured_value,
        ):
            _raise_changed_constraint(class_name, constraint_name)


def validate_inherited_constraints(
    *,
    class_name: str,
    configuration: ConstraintConfiguration,
    parent_configuration: ConstraintConfiguration,
) -> None:
    minimum_valid_value = _minimum_valid_value(configuration)
    maximum_valid_value = _maximum_valid_value(configuration)

    parent_minimum_valid_value = _minimum_valid_value(parent_configuration)
    if parent_minimum_valid_value is not None and (
        minimum_valid_value is None or minimum_valid_value < parent_minimum_valid_value
    ):
        raise BaseTypedIntConstraintConfigurationError(
            f"{class_name} lower bound cannot weaken inherited lower bound "
            f"{parent_minimum_valid_value}."
        )

    parent_maximum_valid_value = _maximum_valid_value(parent_configuration)
    if parent_maximum_valid_value is not None and (
        maximum_valid_value is None or maximum_valid_value > parent_maximum_valid_value
    ):
        raise BaseTypedIntConstraintConfigurationError(
            f"{class_name} upper bound cannot weaken inherited upper bound "
            f"{parent_maximum_valid_value}."
        )

    if parent_configuration.multiple_of is not None and (
        configuration.multiple_of is None
        or configuration.multiple_of % parent_configuration.multiple_of != 0
    ):
        raise BaseTypedIntConstraintConfigurationError(
            f"{class_name}.multiple_of cannot weaken inherited multiple_of="
            f"{parent_configuration.multiple_of}."
        )


def validate_value_constraints(
    *,
    class_name: str,
    value: int,
    configuration: ConstraintConfiguration,
) -> None:
    if configuration.gt is not None and value <= configuration.gt:
        _raise_constraint_violation(class_name, "gt", configuration.gt)

    if configuration.ge is not None and value < configuration.ge:
        _raise_constraint_violation(class_name, "ge", configuration.ge)

    if configuration.lt is not None and value >= configuration.lt:
        _raise_constraint_violation(class_name, "lt", configuration.lt)

    if configuration.le is not None and value > configuration.le:
        _raise_constraint_violation(class_name, "le", configuration.le)

    if configuration.multiple_of is not None and value % configuration.multiple_of != 0:
        _raise_constraint_violation(
            class_name,
            "multiple_of",
            configuration.multiple_of,
        )


def _minimum_valid_value(configuration: ConstraintConfiguration) -> int | None:
    lower_bounds = tuple(
        bound
        for bound in (
            configuration.ge,
            configuration.gt + 1 if configuration.gt is not None else None,
        )
        if bound is not None
    )
    return max(lower_bounds, default=None)


def _maximum_valid_value(configuration: ConstraintConfiguration) -> int | None:
    upper_bounds = tuple(
        bound
        for bound in (
            configuration.le,
            configuration.lt - 1 if configuration.lt is not None else None,
        )
        if bound is not None
    )
    return min(upper_bounds, default=None)


def _validate_constraint_range(
    *,
    class_name: str,
    configuration: ConstraintConfiguration,
) -> None:
    minimum_valid_value = _minimum_valid_value(configuration)
    maximum_valid_value = _maximum_valid_value(configuration)

    if (
        minimum_valid_value is not None
        and maximum_valid_value is not None
        and minimum_valid_value > maximum_valid_value
    ):
        raise BaseTypedIntConstraintConfigurationError(
            f"{class_name} constraints do not permit any integer value."
        )

    if (
        minimum_valid_value is not None
        and maximum_valid_value is not None
        and configuration.multiple_of is not None
    ):
        first_valid_multiple = (
            (minimum_valid_value + configuration.multiple_of - 1)
            // configuration.multiple_of
            * configuration.multiple_of
        )
        if first_valid_multiple > maximum_valid_value:
            raise BaseTypedIntConstraintConfigurationError(
                f"{class_name} constraints do not permit any integer value."
            )


def _integer_declaration_matches(
    *,
    current_value: object,
    configured_value: int | None,
) -> bool:
    if configured_value is None:
        return current_value is None

    return type(current_value) is int and current_value == configured_value


def _raise_changed_constraint(class_name: str, constraint_name: str) -> None:
    raise BaseTypedIntConstraintConfigurationError(
        f"{class_name}.{constraint_name} cannot be changed after class creation. "
        "Declare constraints in the class body."
    )


def _validated_bound_constraint(
    *,
    class_name: str,
    constraint_name: str,
    constraint_value: object,
) -> int | None:
    if constraint_value is None:
        return None

    if type(constraint_value) is not int:
        raise BaseTypedIntConstraintConfigurationError(
            f"{class_name}.{constraint_name} must be int or None. "
            f"Got: {type(constraint_value).__name__}."
        )

    return constraint_value


def _validated_multiple_of_constraint(
    *,
    class_name: str,
    constraint_value: object,
) -> int | None:
    multiple_of = _validated_bound_constraint(
        class_name=class_name,
        constraint_name="multiple_of",
        constraint_value=constraint_value,
    )
    if multiple_of is not None and multiple_of <= 0:
        raise BaseTypedIntConstraintConfigurationError(
            f"{class_name}.multiple_of must be greater than zero. Got: {multiple_of}."
        )

    return multiple_of


def _raise_constraint_violation(
    class_name: str,
    constraint_name: str,
    constraint_value: int,
) -> None:
    raise BaseTypedIntConstraintViolationError(
        f"{class_name} value violates {constraint_name}={constraint_value}."
    )
