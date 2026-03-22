# base-typed-int

Strict typed integer base class with exact runtime subtype preservation and optional Pydantic v2 support.

## Why

`BaseTypedInt` helps model domain integers as explicit runtime types without losing normal `int` behavior.

Example use cases:
- `UserAge`
- `RetryCount`
- `OrderPosition`
- `PriorityLevel`
- `ShardNumber`

This library is designed for cases where plain `int` is too generic, but a full wrapper object would add unnecessary ceremony and runtime overhead.

## Design goals

- exact runtime subtype is preserved
- behaves like plain `int` in normal arithmetic operations
- arithmetic operations usually return plain `int`
- subtype is preserved in containers, attributes, pickle, and Pydantic model fields
- Pydantic serialization exports plain integers
- strict input validation
- `bool` is explicitly rejected
- no extra public API beyond the integer value itself

## Installation

### Core

```bash
pip install base-typed-int
````

### With Pydantic v2 support

```bash
pip install "base-typed-int[pydantic]"
```

### Development

```bash
pip install "base-typed-int[dev]"
```

## Quick start

```python
from base_typed_int import BaseTypedInt


class UserAge(BaseTypedInt):
    pass


class Account:
    def __init__(self, user_age: UserAge) -> None:
        self.user_age: UserAge = user_age


user_age: UserAge = UserAge(18)

assert user_age == 18
assert isinstance(user_age, int)
assert isinstance(user_age, UserAge)
assert type(user_age) is UserAge
assert repr(user_age) == "UserAge(18)"

account: Account = Account(user_age=user_age)
assert account.user_age is user_age
```

## Constructor behavior

`BaseTypedInt` accepts int values and rejects bool explicitly.

```python
from base_typed_int import BaseTypedInt


class RetryCount(BaseTypedInt):
    pass


value_from_int: RetryCount = RetryCount(3)
value_from_typed_int: RetryCount = RetryCount(RetryCount(3))
```

Invalid input raises `BaseTypedIntInvalidInputValueError`.

```python
from base_typed_int import BaseTypedIntInvalidInputValueError


try:
    RetryCount("3")
except BaseTypedIntInvalidInputValueError:
    pass

try:
    RetryCount(True)
except BaseTypedIntInvalidInputValueError:
    pass
```

## Why `bool` is rejected

In Python, `bool` is a subclass of `int`.

```python
assert isinstance(True, int)
assert int(True) == 1
```

That behavior is useful in Python internals, but usually unsafe for domain modeling.
A domain integer such as `RetryCount`, `UserAge`, or `ShardNumber` should not silently accept `True` or `False`.

For that reason, `BaseTypedInt` explicitly rejects `bool` even though `bool` is technically an `int` subtype.

## Runtime behavior

Normal arithmetic keeps standard Python `int` semantics.

```python
class UserAge(BaseTypedInt):
    pass


user_age: UserAge = UserAge(18)

incremented_value: int = user_age + 1
multiplied_value: int = user_age * 2
subtracted_value: int = user_age - 3

assert incremented_value == 19
assert multiplied_value == 36
assert subtracted_value == 15

assert type(incremented_value) is int
assert type(multiplied_value) is int
assert type(subtracted_value) is int
```

This is intentional.
The typed subtype marks the boundary value itself, while regular numeric operations stay native and unsurprising.

## Containers and attributes

The exact subtype instance is preserved when stored and retrieved.

```python
class UserAge(BaseTypedInt):
    pass


class Account:
    def __init__(self, user_age: UserAge) -> None:
        self.user_age: UserAge = user_age


source_user_age: UserAge = UserAge(18)

user_age_list: list[UserAge] = [source_user_age]
user_age_by_field_name: dict[str, UserAge] = {
    "user_age": source_user_age,
}
values_by_user_age: dict[int, str] = {
    source_user_age: "present",
}
account: Account = Account(user_age=source_user_age)

assert user_age_list[0] is source_user_age
assert user_age_by_field_name["user_age"] is source_user_age
assert account.user_age is source_user_age
assert values_by_user_age[source_user_age] == "present"
assert values_by_user_age[18] == "present"
assert type(tuple(values_by_user_age.keys())[0]) is UserAge
```

## Pickle support

Pickle roundtrip preserves the exact subtype.

```python
import pickle

from base_typed_int import BaseTypedInt


class RetryCount(BaseTypedInt):
    pass


source_value: RetryCount = RetryCount(7)
serialized_value: bytes = pickle.dumps(source_value)
restored_value: object = pickle.loads(serialized_value)

assert restored_value == 7
assert isinstance(restored_value, RetryCount)
assert type(restored_value) is RetryCount
```

## JSON behavior

Since `BaseTypedInt` inherits from `int`, standard JSON serialization naturally produces plain JSON numbers.

```python
import json


class RetryCount(BaseTypedInt):
    pass


value: RetryCount = RetryCount(7)
serialized_value: str = json.dumps(value)
restored_value: object = json.loads(serialized_value)

assert serialized_value == "7"
assert restored_value == 7
assert type(restored_value) is int
```

## Pydantic v2 support

`BaseTypedInt` integrates with Pydantic v2 through `__get_pydantic_core_schema__`.

Validation rules:

* accepts only strict integer input
* rejects `bool`
* rejects strings and other non-integer values
* reconstructs the exact runtime subtype

Serialization rules:

* `model_dump()` returns plain integers
* `model_dump_json()` returns JSON numbers

### Example

```python
from pydantic import BaseModel

from base_typed_int import BaseTypedInt


class RetryCount(BaseTypedInt):
    pass


class MetricsModel(BaseModel):
    primary_retry_count: RetryCount
    backup_retry_count: RetryCount


metrics_model: MetricsModel = MetricsModel.model_validate(
    {
        "primary_retry_count": 5,
        "backup_retry_count": 8,
    }
)

assert type(metrics_model.primary_retry_count) is RetryCount
assert type(metrics_model.backup_retry_count) is RetryCount

python_dump: dict[str, object] = metrics_model.model_dump()
json_dump: str = metrics_model.model_dump_json()

assert python_dump == {
    "primary_retry_count": 5,
    "backup_retry_count": 8,
}
assert json_dump == '{"primary_retry_count":5,"backup_retry_count":8}'
```

### Roundtrip from exported payload

```python
source_model: MetricsModel = MetricsModel.model_validate(
    {
        "primary_retry_count": 5,
        "backup_retry_count": 8,
    }
)

python_dump: dict[str, object] = source_model.model_dump()
restored_model: MetricsModel = MetricsModel.model_validate(python_dump)

assert type(restored_model.primary_retry_count) is RetryCount
assert type(restored_model.backup_retry_count) is RetryCount
```

## Error types

```python
from base_typed_int import (
    BaseTypedIntError,
    BaseTypedIntInvalidInputValueError,
    BaseTypedIntInvariantViolationError,
)
```

* `BaseTypedIntError` — root exception for library errors
* `BaseTypedIntInvalidInputValueError` — invalid caller input
* `BaseTypedIntInvariantViolationError` — internal invariant or integration failure

## Testing

```bash
pytest
```

With coverage:

```bash
pytest --cov=base_typed_int --cov-report=term-missing
```

## Type checking

```bash
mypy src tests
pyright
```

## Linting

```bash
ruff check .
ruff format .
```

## Build

```bash
python -m build
```

## Package structure

```text
src/
  base_typed_int/
    __init__.py
    _base_typed_int.py
    _exceptions.py
    py.typed
```

## Compatibility

* Python 3.10+
* CPython
* Pydantic v2 support is optional

## Notes

`BaseTypedInt` is intentionally minimal.
It is not a numeric validation framework and does not enforce domain-specific constraints such as non-negative values, ranges, or upper bounds.

Those constraints should be modeled in your own subclasses or service-layer validation where appropriate.

## License

MIT