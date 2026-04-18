from __future__ import annotations

import pickle

from base_typed_int import BaseTypedInt
from tests.testing_assertions import assert_exact_typed_int_instance
from tests.testing_types import AdminUserAge, UserAge


def test_getnewargs_returns_plain_integer_tuple() -> None:
    typed_value: UserAge = UserAge(18)

    new_arguments: tuple[int] = typed_value.__getnewargs__()

    assert new_arguments == (18,)


def test_reduce_returns_constructor_and_plain_integer_args() -> None:
    typed_value: UserAge = UserAge(18)

    reduced_value: tuple[type[BaseTypedInt], tuple[int]] = typed_value.__reduce__()
    constructor: type[BaseTypedInt]
    constructor_arguments: tuple[int]
    constructor, constructor_arguments = reduced_value

    assert constructor is UserAge
    assert constructor_arguments == (18,)


def test_pickle_roundtrip_preserves_exact_runtime_subtype() -> None:
    source_value: UserAge = UserAge(18)

    serialized_value: bytes = pickle.dumps(source_value)
    restored_value: object = pickle.loads(serialized_value)

    assert_exact_typed_int_instance(
        restored_value,
        expected_plain_value=18,
        expected_type=UserAge,
    )


def test_pickle_roundtrip_preserves_exact_second_level_subtype() -> None:
    source_value: AdminUserAge = AdminUserAge(99)

    serialized_value: bytes = pickle.dumps(source_value)
    restored_value: object = pickle.loads(serialized_value)

    assert_exact_typed_int_instance(
        restored_value,
        expected_plain_value=99,
        expected_type=AdminUserAge,
    )
