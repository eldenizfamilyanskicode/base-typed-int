from __future__ import annotations

import pickle

import pytest

from base_typed_int import BaseTypedInt
from tests.testing_assertions import assert_exact_typed_int_instance
from tests.testing_types import (
    RequestExecutionLeaseTtlMilliseconds,
    SpecializedRequestExecutionLeaseTtlMilliseconds,
)


def test_constrained_getnewargs_returns_plain_integer_tuple() -> None:
    constrained_value = RequestExecutionLeaseTtlMilliseconds(30_000)

    assert constrained_value.__getnewargs__() == (30_000,)


def test_constrained_reduce_returns_exact_constructor_and_plain_integer() -> None:
    constrained_value = RequestExecutionLeaseTtlMilliseconds(30_000)

    reduced_value: tuple[type[BaseTypedInt], tuple[int]] = (
        constrained_value.__reduce__()
    )

    assert reduced_value == (
        RequestExecutionLeaseTtlMilliseconds,
        (30_000,),
    )


@pytest.mark.parametrize("pickle_protocol", range(pickle.HIGHEST_PROTOCOL + 1))
def test_pickle_roundtrip_preserves_exact_constrained_subtype(
    pickle_protocol: int,
) -> None:
    source_value = RequestExecutionLeaseTtlMilliseconds(30_000)

    serialized_value = pickle.dumps(source_value, protocol=pickle_protocol)
    restored_value = pickle.loads(serialized_value)

    assert_exact_typed_int_instance(
        restored_value,
        expected_plain_value=30_000,
        expected_type=RequestExecutionLeaseTtlMilliseconds,
    )


def test_pickle_roundtrip_preserves_exact_second_level_constrained_subtype() -> None:
    source_value = SpecializedRequestExecutionLeaseTtlMilliseconds(30_000)

    serialized_value = pickle.dumps(source_value)
    restored_value = pickle.loads(serialized_value)

    assert_exact_typed_int_instance(
        restored_value,
        expected_plain_value=30_000,
        expected_type=SpecializedRequestExecutionLeaseTtlMilliseconds,
    )
