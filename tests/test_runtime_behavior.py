from __future__ import annotations

import json

from tests.testing_assertions import assert_exact_typed_int_instance
from tests.testing_types import Account, AdminUserAge, UserAge


def test_second_level_subclass_has_plain_integer_runtime_behavior() -> None:
    typed_value: AdminUserAge = AdminUserAge(99)

    incremented_value: int = typed_value + 1
    multiplied_value: int = typed_value * 2
    subtracted_value: int = typed_value - 9

    assert incremented_value == 100
    assert multiplied_value == 198
    assert subtracted_value == 90

    assert type(incremented_value) is int
    assert type(multiplied_value) is int
    assert type(subtracted_value) is int


def test_json_dumps_serializes_typed_int_as_plain_json_number() -> None:
    typed_value: UserAge = UserAge(18)

    serialized_value: str = json.dumps(typed_value)
    restored_value: object = json.loads(serialized_value)

    assert serialized_value == "18"
    assert restored_value == 18
    assert type(restored_value) is int


def test_json_dumps_serializes_zero_typed_int_as_plain_json_number() -> None:
    typed_value: UserAge = UserAge(0)

    serialized_value: str = json.dumps(typed_value)
    restored_value: object = json.loads(serialized_value)

    assert serialized_value == "0"
    assert restored_value == 0
    assert type(restored_value) is int


def test_json_dumps_serializes_nested_payload_values_as_plain_integers() -> None:
    payload: dict[str, object] = {
        "user_age": UserAge(18),
        "admin_user_age": AdminUserAge(99),
        "zero_user_age": UserAge(0),
    }

    serialized_payload: str = json.dumps(payload)
    restored_payload: object = json.loads(serialized_payload)

    assert restored_payload == {
        "user_age": 18,
        "admin_user_age": 99,
        "zero_user_age": 0,
    }


def test_normal_integer_operations_return_plain_int() -> None:
    typed_value: UserAge = UserAge(18)

    incremented_value: int = typed_value + 1
    multiplied_value: int = typed_value * 2
    subtracted_value: int = typed_value - 3

    assert incremented_value == 19
    assert multiplied_value == 36
    assert subtracted_value == 15

    assert type(incremented_value) is int
    assert type(multiplied_value) is int
    assert type(subtracted_value) is int


def test_dict_value_preserves_exact_runtime_subtype_on_store_and_retrieve() -> None:
    typed_value: UserAge = UserAge(18)

    values_by_field_name: dict[str, UserAge] = {"user_age": typed_value}

    retrieved_value: UserAge = values_by_field_name["user_age"]

    assert retrieved_value is typed_value
    assert_exact_typed_int_instance(
        retrieved_value,
        expected_plain_value=18,
        expected_type=UserAge,
    )


def test_typed_int_key_is_retrievable_by_plain_int_key() -> None:
    typed_key: UserAge = UserAge(18)
    values_by_user_age: dict[int, str] = {typed_key: "present"}

    retrieved_by_typed_key: str = values_by_user_age[typed_key]
    retrieved_by_plain_int_key: str = values_by_user_age[18]

    stored_keys: list[int] = list(values_by_user_age.keys())
    stored_key: int = stored_keys[0]

    assert retrieved_by_typed_key == "present"
    assert retrieved_by_plain_int_key == "present"
    assert stored_key is typed_key
    assert_exact_typed_int_instance(
        stored_key,
        expected_plain_value=18,
        expected_type=UserAge,
    )


def test_typed_int_has_same_hash_and_equality_as_plain_int() -> None:
    typed_value: UserAge = UserAge(18)
    plain_value: int = 18

    assert typed_value == plain_value
    assert hash(typed_value) == hash(plain_value)


def test_repr_uses_exact_runtime_subtype_name_and_plain_integer_value() -> None:
    typed_value: AdminUserAge = AdminUserAge(99)

    rendered_value: str = repr(typed_value)

    assert rendered_value == "AdminUserAge(99)"


def test_plain_class_attribute_preserves_exact_runtime_subtype() -> None:
    typed_value: UserAge = UserAge(18)

    account: Account = Account(user_age=typed_value)

    retrieved_value: UserAge = account.user_age

    assert retrieved_value is typed_value
    assert_exact_typed_int_instance(
        retrieved_value,
        expected_plain_value=18,
        expected_type=UserAge,
    )
