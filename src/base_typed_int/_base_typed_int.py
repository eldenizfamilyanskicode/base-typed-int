from __future__ import annotations

from typing import Any, TypeVar

from ._exceptions import (
    BaseTypedIntInvalidInputValueError,
    BaseTypedIntInvariantViolationError,
)

BaseTypedIntType = TypeVar(
    "BaseTypedIntType",
    bound="BaseTypedInt",
)


class BaseTypedInt(int):
    """
    Transparent domain-typed integer.

    Design rules:
    - stores an exact runtime subtype
    - behaves like plain int in normal numeric operations
    - normal numeric operations usually return plain int
    - preserves subtype in containers, pickle, and Pydantic model fields
    - does not introduce extra public domain-specific API
    - accepts only real int input and rejects bool explicitly
    """

    __slots__ = ()

    def __new__(
        cls: type[BaseTypedIntType],
        value: int,
    ) -> BaseTypedIntType:
        if isinstance(value, bool):
            raise BaseTypedIntInvalidInputValueError(
                "BaseTypedInt must be initialized only with int. "
                "bool is not allowed. "
                f"Got: {type(value).__name__}."
            )

        if not isinstance(value, int):  # pyright: ignore[reportUnnecessaryIsInstance] runtime boundary guard
            raise BaseTypedIntInvalidInputValueError(
                "BaseTypedInt must be initialized only with int. "
                f"Got: {type(value).__name__}."
            )

        return int.__new__(cls, value)

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,
        handler: Any,
    ) -> Any:
        """
        Provide Pydantic v2 validation and serialization.

        Validation:
        - accepts only strict int input
        - rejects bool and all non-int input values
        - returns the exact subclass instance

        Serialization:
        - serializes as plain int
        """
        del source_type
        del handler

        try:
            from pydantic_core import (  # pyright: ignore[reportMissingImports]
                core_schema,
            )
        except ImportError as import_error:
            raise BaseTypedIntInvariantViolationError(
                "pydantic-core is required to build BaseTypedInt schema."
            ) from import_error

        def serialize_to_plain_int(value: BaseTypedInt) -> int:
            return int(value)

        return core_schema.no_info_after_validator_function(
            cls,
            core_schema.int_schema(strict=True),
            serialization=core_schema.plain_serializer_function_ser_schema(
                serialize_to_plain_int,
                return_schema=core_schema.int_schema(),
            ),
        )

    def __getnewargs__(self) -> tuple[int]:
        return (int(self),)

    def __reduce__(
        self,
    ) -> tuple[type[BaseTypedInt], tuple[int]]:
        return (self.__class__, (int(self),))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({int(self)!r})"
