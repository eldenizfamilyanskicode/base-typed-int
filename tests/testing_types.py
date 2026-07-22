from __future__ import annotations

from base_typed_int import BaseConstrainedTypedInt, BaseTypedInt


class UserAge(BaseTypedInt):
    pass


class AdminUserAge(UserAge):
    pass


class RetryCount(BaseTypedInt):
    pass


class RequestExecutionLeaseTtlMilliseconds(BaseConstrainedTypedInt):
    ge = 1_000
    le = 3_600_000
    multiple_of = 1_000


class SpecializedRequestExecutionLeaseTtlMilliseconds(
    RequestExecutionLeaseTtlMilliseconds
):
    pass


class Account:
    def __init__(self, user_age: UserAge) -> None:
        self.user_age: UserAge = user_age
