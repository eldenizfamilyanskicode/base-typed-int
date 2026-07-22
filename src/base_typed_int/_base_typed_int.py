from __future__ import annotations

from typing import Any, TypeVar

from base_typed_int._exceptions import BaseTypedIntInvalidInputValueError
from base_typed_int._pydantic_support import (
    build_typed_int_pydantic_core_schema,
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

        return int.__new__(cls, int.__int__(value))

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

        return build_typed_int_pydantic_core_schema(cls)

    def __getnewargs__(self) -> tuple[int]:
        return (int.__int__(self),)

    def __reduce__(
        self,
    ) -> tuple[type[BaseTypedInt], tuple[int]]:
        return (self.__class__, (int.__int__(self),))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({int.__int__(self)!r})"
