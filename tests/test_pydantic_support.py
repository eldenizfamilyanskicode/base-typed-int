from __future__ import annotations

import pytest

pytest.importorskip("pydantic")
pytest.importorskip("pydantic_core")

from pydantic import BaseModel, ValidationError

from tests.testing_assertions import assert_exact_typed_int_instance
from tests.testing_types import AdminUserAge, RetryCount


class ExampleModel(BaseModel):
    value: RetryCount


class MetricsModel(BaseModel):
    primary_retry_count: RetryCount
    retry_list: list[RetryCount]
    retry_tuple: tuple[RetryCount, ...]
    retry_mapping: dict[str, RetryCount]


class AdminExampleModel(BaseModel):
    value: AdminUserAge


def test_pydantic_preserves_exact_second_level_subtype() -> None:
    model: AdminExampleModel = AdminExampleModel.model_validate({"value": 99})

    assert_exact_typed_int_instance(
        model.value,
        expected_plain_value=99,
        expected_type=AdminUserAge,
    )


def test_pydantic_accepts_zero() -> None:
    model: ExampleModel = ExampleModel.model_validate({"value": 0})

    assert_exact_typed_int_instance(
        model.value,
        expected_plain_value=0,
        expected_type=RetryCount,
    )


def test_pydantic_accepts_plain_integer_and_returns_exact_subtype() -> None:
    model: ExampleModel = ExampleModel.model_validate({"value": 7})

    assert_exact_typed_int_instance(
        model.value,
        expected_plain_value=7,
        expected_type=RetryCount,
    )


def test_pydantic_accepts_existing_typed_int_instance() -> None:
    typed_value: RetryCount = RetryCount(7)

    model: ExampleModel = ExampleModel.model_validate({"value": typed_value})

    assert_exact_typed_int_instance(
        model.value,
        expected_plain_value=7,
        expected_type=RetryCount,
    )


def test_pydantic_rejects_string_input() -> None:
    with pytest.raises(ValidationError):
        ExampleModel.model_validate({"value": "7"})


def test_pydantic_rejects_bool_input() -> None:
    with pytest.raises(ValidationError):
        ExampleModel.model_validate({"value": True})


def test_pydantic_preserves_exact_runtime_subtypes_in_nested_data_structures() -> None:
    input_payload: dict[str, object] = {
        "primary_retry_count": 10,
        "retry_list": [11],
        "retry_tuple": (12,),
        "retry_mapping": {"background_job": 13},
    }

    model: MetricsModel = MetricsModel.model_validate(input_payload)

    assert_exact_typed_int_instance(
        model.primary_retry_count,
        expected_plain_value=10,
        expected_type=RetryCount,
    )
    assert_exact_typed_int_instance(
        model.retry_list[0],
        expected_plain_value=11,
        expected_type=RetryCount,
    )
    assert_exact_typed_int_instance(
        model.retry_tuple[0],
        expected_plain_value=12,
        expected_type=RetryCount,
    )
    assert_exact_typed_int_instance(
        model.retry_mapping["background_job"],
        expected_plain_value=13,
        expected_type=RetryCount,
    )


def test_pydantic_serializes_to_plain_integers() -> None:
    model: MetricsModel = MetricsModel.model_validate(
        {
            "primary_retry_count": 10,
            "retry_list": [11],
            "retry_tuple": (12,),
            "retry_mapping": {"background_job": 13},
        }
    )

    dumped_python: dict[str, object] = model.model_dump()
    dumped_json: str = model.model_dump_json()

    assert dumped_python == {
        "primary_retry_count": 10,
        "retry_list": [11],
        "retry_tuple": (12,),
        "retry_mapping": {"background_job": 13},
    }
    assert dumped_json == (
        '{"primary_retry_count":10,'
        '"retry_list":[11],'
        '"retry_tuple":[12],'
        '"retry_mapping":{"background_job":13}}'
    )