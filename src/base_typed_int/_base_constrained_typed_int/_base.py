from __future__ import annotations

from typing import Any, ClassVar, TypeVar

import base_typed_int._base_constrained_typed_int._constraints as _constraints
from base_typed_int._base_typed_int import BaseTypedInt
from base_typed_int._exceptions import (
    BaseTypedIntConstraintConfigurationError,
    BaseTypedIntInvariantViolationError,
)
from base_typed_int._pydantic_support import build_typed_int_pydantic_core_schema

BaseConstrainedTypedIntType = TypeVar(
    "BaseConstrainedTypedIntType",
    bound="BaseConstrainedTypedInt",
)


def _effective_constraint_configuration(
    typed_int_type: type[BaseConstrainedTypedInt],
) -> _constraints.ConstraintConfiguration:
    configuration = _stored_constraint_configuration(typed_int_type)

    for constrained_type in typed_int_type.__mro__:
        if not issubclass(constrained_type, BaseConstrainedTypedInt):
            continue

        constrained_configuration = _stored_constraint_configuration(constrained_type)
        _constraints.validate_constraint_declaration_unchanged(
            class_name=constrained_type.__name__,
            configuration=constrained_configuration,
            current_gt=constrained_type.gt,
            current_ge=constrained_type.ge,
            current_lt=constrained_type.lt,
            current_le=constrained_type.le,
            current_multiple_of=constrained_type.multiple_of,
        )

    return configuration


def _stored_constraint_configuration(
    typed_int_type: type[BaseConstrainedTypedInt],
) -> _constraints.ConstraintConfiguration:
    configuration_value: object = vars(typed_int_type).get("_constraint_configuration")
    if not isinstance(configuration_value, _constraints.ConstraintConfiguration):
        raise BaseTypedIntInvariantViolationError(
            f"{typed_int_type.__name__} internal constraint configuration is invalid."
        )

    return configuration_value


def _single_constrained_parent_type(
    typed_int_type: type[BaseConstrainedTypedInt],
) -> type[BaseConstrainedTypedInt]:
    constrained_parent_types: list[type[BaseConstrainedTypedInt]] = []
    for parent_type in typed_int_type.__bases__:
        if issubclass(parent_type, BaseConstrainedTypedInt):
            constrained_parent_types.append(parent_type)

    # CPython 3.10 and 3.11 reject these bases before __init_subclass__.
    if len(constrained_parent_types) > 1:  # pragma: no cover
        parent_type_names = ", ".join(
            parent_type.__name__ for parent_type in constrained_parent_types
        )
        raise BaseTypedIntConstraintConfigurationError(
            f"{typed_int_type.__name__} cannot inherit from multiple constrained "
            f"integer types: {parent_type_names}. Declare "
            f"{typed_int_type.__name__} directly from BaseConstrainedTypedInt "
            "with its own constraints."
        )

    return constrained_parent_types[0]


class BaseConstrainedTypedInt(BaseTypedInt):
    """
    Callable domain-typed integer with declarative value constraints.

    Subclasses may declare ``gt``, ``ge``, ``lt``, ``le``, and ``multiple_of``
    as class attributes. Construction accepts only ``int`` except ``bool``,
    validates every declared constraint, and returns the exact subclass.
    Constraint declarations cannot be changed after class creation and may only
    become stricter in subclasses. A subclass may have only one constrained
    integer parent; combined concepts must declare their own constraints.

    The class performs no coercion and does not require Pydantic for direct use.
    """

    __slots__ = ()

    gt: ClassVar[int | None] = None
    ge: ClassVar[int | None] = None
    lt: ClassVar[int | None] = None
    le: ClassVar[int | None] = None
    multiple_of: ClassVar[int | None] = None

    _constraint_configuration: ClassVar[_constraints.ConstraintConfiguration] = (
        _constraints.EMPTY_CONSTRAINT_CONFIGURATION
    )

    def __init_subclass__(cls, **kwargs: Any) -> None:
        constrained_parent_type = _single_constrained_parent_type(cls)
        super().__init_subclass__(**kwargs)

        parent_configuration = _effective_constraint_configuration(
            constrained_parent_type
        )
        configuration = _constraints.build_effective_constraint_configuration(
            class_name=cls.__name__,
            class_namespace=vars(cls),
            parent_configuration=parent_configuration,
        )

        type.__setattr__(cls, "gt", configuration.gt)
        type.__setattr__(cls, "ge", configuration.ge)
        type.__setattr__(cls, "lt", configuration.lt)
        type.__setattr__(cls, "le", configuration.le)
        type.__setattr__(cls, "multiple_of", configuration.multiple_of)
        type.__setattr__(
            cls,
            "_constraint_configuration",
            configuration,
        )

    def __new__(
        cls: type[BaseConstrainedTypedIntType],
        value: int,
    ) -> BaseConstrainedTypedIntType:
        typed_value: BaseConstrainedTypedIntType = super().__new__(cls, value)
        _constraints.validate_value_constraints(
            class_name=cls.__name__,
            value=int.__int__(typed_value),
            configuration=_effective_constraint_configuration(cls),
        )
        return typed_value

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: Any,
    ) -> Any:
        """Build a strict constrained integer schema returning the exact subtype."""
        del source_type
        del handler

        configuration = _effective_constraint_configuration(cls)

        def validate_configuration() -> None:
            _effective_constraint_configuration(cls)

        return build_typed_int_pydantic_core_schema(
            cls,
            gt=configuration.gt,
            ge=configuration.ge,
            lt=configuration.lt,
            le=configuration.le,
            multiple_of=configuration.multiple_of,
            configuration_validator=validate_configuration,
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls,
        core_schema: Any,
        handler: Any,
    ) -> Any:
        """Validate sealed constraints before returning generated JSON Schema."""
        _effective_constraint_configuration(cls)
        return handler(core_schema)
