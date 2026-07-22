from __future__ import annotations

from collections.abc import Callable
from typing import Any

from base_typed_int._exceptions import BaseTypedIntInvariantViolationError


def build_typed_int_pydantic_core_schema(
    typed_int_type: type[int],
    *,
    gt: int | None = None,
    ge: int | None = None,
    lt: int | None = None,
    le: int | None = None,
    multiple_of: int | None = None,
    configuration_validator: Callable[[], None] | None = None,
) -> Any:
    """Build a strict Pydantic v2 schema for one concrete typed integer class."""
    try:
        from pydantic_core import (  # pyright: ignore[reportMissingImports]
            PydanticKnownError,
            PydanticSerializationError,
            core_schema,
        )
    except ImportError as import_error:
        raise BaseTypedIntInvariantViolationError(
            f"pydantic-core is required to build {typed_int_type.__name__} schema."
        ) from import_error

    def require_integer_instance(value: object) -> int:
        if configuration_validator is not None:
            configuration_validator()

        if isinstance(value, bool) or not isinstance(value, int):
            raise PydanticKnownError("int_type")

        return int.__int__(value)

    def serialize_to_plain_integer(value: object) -> int:
        if configuration_validator is not None:
            configuration_validator()

        if not isinstance(value, typed_int_type):
            raise PydanticSerializationError(
                f"Expected {typed_int_type.__name__} during serialization. "
                f"Got: {type(value).__name__}."
            )

        return int.__int__(value)

    integer_schema: Any = core_schema.int_schema(
        strict=True,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        multiple_of=multiple_of,
    )
    input_schema: Any = core_schema.no_info_before_validator_function(
        require_integer_instance,
        integer_schema,
    )

    return core_schema.no_info_after_validator_function(
        typed_int_type,
        input_schema,
        serialization=core_schema.plain_serializer_function_ser_schema(
            serialize_to_plain_integer,
            return_schema=core_schema.int_schema(
                strict=True,
                gt=gt,
                ge=ge,
                lt=lt,
                le=le,
                multiple_of=multiple_of,
            ),
        ),
    )
