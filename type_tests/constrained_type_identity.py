from __future__ import annotations

from typing_extensions import assert_type

from base_typed_int import BaseConstrainedTypedInt


class RequestExecutionAttemptEpoch(BaseConstrainedTypedInt):
    ge = 1


def consume_attempt_epoch(value: RequestExecutionAttemptEpoch) -> None:
    assert_type(value, RequestExecutionAttemptEpoch)


def test_constrained_class_is_annotation_and_constructor() -> None:
    attempt_epoch: RequestExecutionAttemptEpoch = RequestExecutionAttemptEpoch(1)

    assert_type(attempt_epoch, RequestExecutionAttemptEpoch)
    consume_attempt_epoch(attempt_epoch)
