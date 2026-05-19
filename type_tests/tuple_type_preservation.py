from __future__ import annotations

from typing_extensions import assert_type

from base_typed_int import BaseTypedInt


class UserAge(BaseTypedInt):
    pass


def test_tuple_preserves_typed_int_from_exactly_typed_list() -> None:
    source_user_age: UserAge = UserAge(18)
    user_age_list: list[UserAge] = [source_user_age]

    user_age_tuple: tuple[UserAge, ...] = tuple(user_age_list)
    retrieved_user_age: UserAge = user_age_tuple[0]

    assert_type(user_age_tuple, tuple[UserAge, ...])
    assert_type(retrieved_user_age, UserAge)


def test_tuple_preserves_typed_int_from_exactly_typed_dict_keys() -> None:
    source_user_age: UserAge = UserAge(18)
    values_by_exact_user_age: dict[UserAge, str] = {
        source_user_age: "present",
    }

    stored_keys: tuple[UserAge, ...] = tuple(values_by_exact_user_age.keys())
    stored_key: UserAge = stored_keys[0]

    assert_type(stored_keys, tuple[UserAge, ...])
    assert_type(stored_key, UserAge)


def test_tuple_from_plain_int_typed_dict_keys_is_int_by_design() -> None:
    source_user_age: UserAge = UserAge(18)
    values_by_plain_int: dict[int, str] = {
        source_user_age: "present",
    }

    stored_keys: tuple[int, ...] = tuple(values_by_plain_int.keys())
    stored_key: int = stored_keys[0]

    assert_type(stored_keys, tuple[int, ...])
    assert_type(stored_key, int)
