from __future__ import annotations

import json

import pytest

pytest.importorskip("pydantic")
pytest.importorskip("pydantic_core")

from pydantic import BaseModel, TypeAdapter, ValidationError
from pydantic_core import PydanticSerializationError

from base_typed_int import (
    BaseConstrainedTypedInt,
    BaseTypedInt,
    BaseTypedIntConstraintConfigurationError,
)
from tests.testing_assertions import assert_exact_typed_int_instance
from tests.testing_types import (
    RequestExecutionLeaseTtlMilliseconds,
    SpecializedRequestExecutionLeaseTtlMilliseconds,
)


class LeaseModel(BaseModel):
    value: RequestExecutionLeaseTtlMilliseconds


class NestedLeaseModel(BaseModel):
    primary_lease: RequestExecutionLeaseTtlMilliseconds
    lease_list: list[RequestExecutionLeaseTtlMilliseconds]
    lease_mapping: dict[str, RequestExecutionLeaseTtlMilliseconds]


class SpecializedLeaseModel(BaseModel):
    value: SpecializedRequestExecutionLeaseTtlMilliseconds


class ExclusiveRangeInt(BaseConstrainedTypedInt):
    gt = 0
    lt = 10


class ExclusiveRangeModel(BaseModel):
    value: ExclusiveRangeInt


class MutationDetectedParentInt(BaseConstrainedTypedInt):
    ge = 1


class MutationDetectedInt(MutationDetectedParentInt):
    pass


VALID_LEASE = 30_000


def test_pydantic_accepts_valid_integer_and_returns_exact_constrained_subtype() -> None:
    model = LeaseModel.model_validate({"value": VALID_LEASE})

    assert_exact_typed_int_instance(
        model.value,
        expected_plain_value=VALID_LEASE,
        expected_type=RequestExecutionLeaseTtlMilliseconds,
    )


def test_pydantic_preserves_exact_second_level_constrained_subtype() -> None:
    model = SpecializedLeaseModel.model_validate({"value": VALID_LEASE})

    assert_exact_typed_int_instance(
        model.value,
        expected_plain_value=VALID_LEASE,
        expected_type=SpecializedRequestExecutionLeaseTtlMilliseconds,
    )


def test_pydantic_accepts_existing_constrained_instance() -> None:
    source_value = RequestExecutionLeaseTtlMilliseconds(VALID_LEASE)

    model = LeaseModel.model_validate({"value": source_value})

    assert_exact_typed_int_instance(
        model.value,
        expected_plain_value=VALID_LEASE,
        expected_type=RequestExecutionLeaseTtlMilliseconds,
    )


def test_pydantic_reconstructs_child_as_exact_declared_parent_type() -> None:
    source_value = SpecializedRequestExecutionLeaseTtlMilliseconds(VALID_LEASE)

    model = LeaseModel.model_validate({"value": source_value})

    assert type(model.value) is RequestExecutionLeaseTtlMilliseconds
    assert model.value == VALID_LEASE


def test_pydantic_converts_other_typed_integer_to_exact_target_type() -> None:
    source_value = BaseTypedInt(VALID_LEASE)

    model = LeaseModel.model_validate({"value": source_value})

    assert_exact_typed_int_instance(
        model.value,
        expected_plain_value=VALID_LEASE,
        expected_type=RequestExecutionLeaseTtlMilliseconds,
    )


@pytest.mark.parametrize(
    ("model_type", "invalid_value", "expected_error_type"),
    [
        (LeaseModel, 0, "greater_than_equal"),
        (LeaseModel, 3_601_000, "less_than_equal"),
        (LeaseModel, 1_001, "multiple_of"),
        (ExclusiveRangeModel, 0, "greater_than"),
        (ExclusiveRangeModel, 10, "less_than"),
    ],
)
def test_pydantic_rejects_each_constraint_violation(
    model_type: type[BaseModel],
    invalid_value: int,
    expected_error_type: str,
) -> None:
    with pytest.raises(ValidationError) as caught_error:
        model_type.model_validate({"value": invalid_value})

    assert caught_error.value.errors()[0]["type"] == expected_error_type


@pytest.mark.parametrize("invalid_value", [True, False, "30000", 30_000.0])
def test_pydantic_strictly_rejects_non_integer_input(invalid_value: object) -> None:
    with pytest.raises(ValidationError) as caught_error:
        LeaseModel.model_validate({"value": invalid_value})

    assert caught_error.value.errors()[0]["type"] == "int_type"


def test_non_strict_pydantic_call_cannot_override_integer_only_contract() -> None:
    constrained_adapter = TypeAdapter(RequestExecutionLeaseTtlMilliseconds)
    base_adapter = TypeAdapter(BaseTypedInt)

    with pytest.raises(ValidationError):
        constrained_adapter.validate_python("30000", strict=False)

    with pytest.raises(ValidationError):
        base_adapter.validate_python("7", strict=False)


def test_pydantic_revalidates_forged_constrained_instance() -> None:
    adapter = TypeAdapter(RequestExecutionLeaseTtlMilliseconds)
    forged_invalid_value = int.__new__(RequestExecutionLeaseTtlMilliseconds, 0)

    with pytest.raises(ValidationError) as caught_error:
        adapter.validate_python(forged_invalid_value)

    assert caught_error.value.errors()[0]["type"] == "greater_than_equal"


def test_cached_pydantic_schema_rejects_changed_constraint_declaration() -> None:
    adapter = TypeAdapter(MutationDetectedInt)
    source_value = MutationDetectedInt(1)

    MutationDetectedParentInt.ge = 2
    try:
        with pytest.raises(ValidationError, match="cannot be changed"):
            adapter.validate_python(2)

        with pytest.raises(PydanticSerializationError, match="cannot be changed"):
            adapter.dump_python(source_value)

        with pytest.raises(
            BaseTypedIntConstraintConfigurationError,
            match="cannot be changed",
        ):
            adapter.json_schema()
    finally:
        MutationDetectedParentInt.ge = 1


def test_pydantic_preserves_exact_subtype_in_nested_containers() -> None:
    model = NestedLeaseModel.model_validate(
        {
            "primary_lease": VALID_LEASE,
            "lease_list": [VALID_LEASE],
            "lease_mapping": {"request": VALID_LEASE},
        }
    )

    assert type(model.primary_lease) is RequestExecutionLeaseTtlMilliseconds
    assert type(model.lease_list[0]) is RequestExecutionLeaseTtlMilliseconds
    assert type(model.lease_mapping["request"]) is RequestExecutionLeaseTtlMilliseconds


def test_pydantic_model_validate_json_constructs_exact_subtype() -> None:
    json_payload = json.dumps({"value": VALID_LEASE})

    model = LeaseModel.model_validate_json(json_payload)

    assert type(model.value) is RequestExecutionLeaseTtlMilliseconds
    assert model.value == VALID_LEASE


def test_pydantic_serializes_constrained_values_as_plain_integers() -> None:
    model = LeaseModel.model_validate({"value": VALID_LEASE})

    dumped_python = model.model_dump()
    dumped_json = model.model_dump_json()

    assert dumped_python == {"value": VALID_LEASE}
    assert type(dumped_python["value"]) is int
    assert dumped_json == f'{{"value":{VALID_LEASE}}}'


def test_pydantic_serialization_rejects_wrong_runtime_type() -> None:
    invalid_model = LeaseModel.model_construct(value=VALID_LEASE)

    with pytest.raises(PydanticSerializationError, match="Expected"):
        invalid_model.model_dump()


def test_type_adapter_returns_exact_constrained_subtype() -> None:
    adapter = TypeAdapter(RequestExecutionLeaseTtlMilliseconds)

    constrained_value = adapter.validate_python(VALID_LEASE)

    assert_exact_typed_int_instance(
        constrained_value,
        expected_plain_value=VALID_LEASE,
        expected_type=RequestExecutionLeaseTtlMilliseconds,
    )


def test_json_schema_exposes_inclusive_and_multiple_constraints() -> None:
    value_schema = LeaseModel.model_json_schema()["properties"]["value"]

    assert value_schema == {
        "maximum": 3_600_000,
        "minimum": 1_000,
        "multipleOf": 1_000,
        "title": "Value",
        "type": "integer",
    }


def test_json_schema_exposes_exclusive_constraints() -> None:
    value_schema = ExclusiveRangeModel.model_json_schema()["properties"]["value"]

    assert value_schema == {
        "exclusiveMaximum": 10,
        "exclusiveMinimum": 0,
        "title": "Value",
        "type": "integer",
    }


def test_validation_and_serialization_json_schemas_expose_constraints() -> None:
    adapter = TypeAdapter(RequestExecutionLeaseTtlMilliseconds)

    validation_schema = adapter.json_schema(mode="validation")
    serialization_schema = adapter.json_schema(mode="serialization")

    expected_schema = {
        "maximum": 3_600_000,
        "minimum": 1_000,
        "multipleOf": 1_000,
        "type": "integer",
    }
    assert validation_schema == expected_schema
    assert serialization_schema == expected_schema
