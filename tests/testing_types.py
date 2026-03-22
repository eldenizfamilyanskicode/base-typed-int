from __future__ import annotations

from base_typed_int import BaseTypedInt


class UserAge(BaseTypedInt):
    pass


class AdminUserAge(UserAge):
    pass


class RetryCount(BaseTypedInt):
    pass


class Account:
    def __init__(self, user_age: UserAge) -> None:
        self.user_age: UserAge = user_age