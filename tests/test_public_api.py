from __future__ import annotations

import inspect
from importlib.metadata import version

import base_typed_int
from base_typed_int import (
    BaseConstrainedTypedInt,
    BaseTypedInt,
    BaseTypedIntConstraintConfigurationError,
    BaseTypedIntConstraintViolationError,
    BaseTypedIntError,
    BaseTypedIntInvalidInputValueError,
    BaseTypedIntInvariantViolationError,
)


def test_public_api_exports_both_base_classes_and_all_package_errors() -> None:
    expected_export_names = [
        "BaseConstrainedTypedInt",
        "BaseTypedInt",
        "BaseTypedIntConstraintConfigurationError",
        "BaseTypedIntConstraintViolationError",
        "BaseTypedIntError",
        "BaseTypedIntInvalidInputValueError",
        "BaseTypedIntInvariantViolationError",
    ]
    expected_export_values = [
        BaseConstrainedTypedInt,
        BaseTypedInt,
        BaseTypedIntConstraintConfigurationError,
        BaseTypedIntConstraintViolationError,
        BaseTypedIntError,
        BaseTypedIntInvalidInputValueError,
        BaseTypedIntInvariantViolationError,
    ]

    assert base_typed_int.__all__ == expected_export_names
    assert [
        getattr(base_typed_int, export_name) for export_name in expected_export_names
    ] == expected_export_values


def test_constrained_base_is_a_real_callable_integer_class() -> None:
    assert inspect.isclass(BaseConstrainedTypedInt)
    assert callable(BaseConstrainedTypedInt)
    assert issubclass(BaseConstrainedTypedInt, BaseTypedInt)
    assert issubclass(BaseConstrainedTypedInt, int)
    assert (
        BaseConstrainedTypedInt.__module__
        == "base_typed_int._base_constrained_typed_int._base"
    )


def test_runtime_version_matches_installed_project_metadata() -> None:
    assert base_typed_int.__version__ == version("base-typed-int")
