# base-typed-int

`base_typed_int` is a small Python library for building domain-specific integer types that remain real `int` objects at runtime.

Callable branded and constrained integer base classes with exact runtime subtype preservation and optional Pydantic v2 support.

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
- optional intrinsic `gt`, `ge`, `lt`, `le`, and `multiple_of` constraints
- declared constraints appear in Pydantic-generated JSON Schema

## Installation

### Core

```bash
pip install base-typed-int
```

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

## Constrained typed integers

Use `BaseConstrainedTypedInt` when numeric rules belong to the named domain type
itself:

```python
from base_typed_int import BaseConstrainedTypedInt


class RequestExecutionLeaseTtlMilliseconds(BaseConstrainedTypedInt):
    ge = 1_000
    le = 3_600_000


lease_ttl = RequestExecutionLeaseTtlMilliseconds(30_000)

assert type(lease_ttl) is RequestExecutionLeaseTtlMilliseconds
assert isinstance(lease_ttl, int)
```

The public symbol is a real, callable class. Construction validates the value
even when Pydantic is not installed:

```python
from base_typed_int import BaseTypedIntConstraintViolationError


try:
    RequestExecutionLeaseTtlMilliseconds(500)
except BaseTypedIntConstraintViolationError:
    pass
```

### Constraint properties

| Property | Meaning |
| --- | --- |
| `gt` | Value must be strictly greater than this integer |
| `ge` | Value must be greater than or equal to this integer |
| `lt` | Value must be strictly less than this integer |
| `le` | Value must be less than or equal to this integer |
| `multiple_of` | Value must be divisible by this positive integer |

Every property defaults to `None`. Bounds may be negative or zero, while
`multiple_of` must be greater than zero. Invalid declarations and constraint
sets that permit no integer fail when the class is defined.

Constraint declarations are sealed when the class is created because Pydantic
caches schemas. Declare them in the class body. Changing or deleting an effective
value later is rejected the next time the class is constructed, validated,
serialized, or used to build a schema. Detection on use avoids imposing a custom
metaclass, so constrained types remain compatible with `ABC` and independently
metaclassed bases.

A constrained subtype may only narrow its inherited domain: lower bounds may
rise, upper bounds may fall, and `multiple_of` may become a multiple of the
inherited value. A class may inherit from only one constrained integer type.
Multiple constrained parents are rejected because composing their constraints
would silently assign several domain meanings to a different value type.

Declare a combined invariant as an independent type instead:

```python
class EvenInt(BaseConstrainedTypedInt):
    multiple_of = 2


class DivisibleByThreeInt(BaseConstrainedTypedInt):
    multiple_of = 3


# Rejected: this gives one value type two domain parents.
class DivisibleBySixInt(EvenInt, DivisibleByThreeInt):
    pass


# Declare the new value type and its own invariant explicitly.
class DivisibleBySixInt(BaseConstrainedTypedInt):
    multiple_of = 6
```

### Canonical declaration for coding agents

When constraints are invariants of a named domain integer, declare one public
class:

```python
from base_typed_int import BaseConstrainedTypedInt


class RequestExecutionAttemptEpoch(BaseConstrainedTypedInt):
    ge = 1
```

Do not create a public `Annotated` type alias for the same concept:

```python
from typing import Annotated

from pydantic import Field

from base_typed_int import BaseTypedInt


class RequestExecutionAttemptEpoch(BaseTypedInt):
    pass


# Avoid this for invariants of a named domain type (Python 3.12+).
type PositiveRequestExecutionAttemptEpoch = Annotated[
    RequestExecutionAttemptEpoch,
    Field(ge=1),
]
```

A PEP 695 `type` alias is not a class: it is not the reusable constructor or
runtime identity of the domain concept. Put every reusable invariant on the
`BaseConstrainedTypedInt` subclass. `Annotated[int, ...]` remains appropriate
for a local field constraint that does not define a reusable branded type.

The constrained class is both annotation and constructor:

```python
def start_attempt(value: RequestExecutionAttemptEpoch) -> None:
    ...


start_attempt(RequestExecutionAttemptEpoch(1))  # accepted
start_attempt(1)  # static type error
```

## Constructor behavior

The constructor is typed as accepting `int`, while still keeping a runtime validation guard for invalid non-integer inputs crossing dynamic boundaries.

```python
from base_typed_int import BaseTypedInt

class RetryCount(BaseTypedInt):
    pass


value_from_int: RetryCount = RetryCount(3)
value_from_typed_int: RetryCount = RetryCount(RetryCount(3))
```

Invalid input raises `BaseTypedIntInvalidInputValueError`.

```python
from base_typed_int import (
    BaseTypedInt,
    BaseTypedIntInvalidInputValueError,
)

class RetryCount(BaseTypedInt):
    pass

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
from base_typed_int import BaseTypedInt

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
from base_typed_int import BaseTypedInt

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

from base_typed_int import BaseTypedInt

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

Both base classes integrate with Pydantic v2 through
`__get_pydantic_core_schema__`.

Validation rules:

* accepts only strict integer input
* rejects `bool`
* rejects strings and other non-integer values
* reconstructs the exact runtime subtype
* applies intrinsic constrained-class rules without `Annotated` or `Field`

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

### Constrained Pydantic fields

Constrained classes are used directly as field annotations:

```python
from pydantic import BaseModel


class LeaseModel(BaseModel):
    lease_ttl: RequestExecutionLeaseTtlMilliseconds


lease_model = LeaseModel.model_validate({"lease_ttl": 30_000})

assert type(lease_model.lease_ttl) is RequestExecutionLeaseTtlMilliseconds
assert LeaseModel.model_json_schema()["properties"]["lease_ttl"]["minimum"] == 1_000
assert LeaseModel.model_json_schema()["properties"]["lease_ttl"]["maximum"] == 3_600_000
```

## Error types

```python
from base_typed_int import (
    BaseConstrainedTypedInt,
    BaseTypedIntConstraintConfigurationError,
    BaseTypedIntConstraintViolationError,
    BaseTypedIntError,
    BaseTypedIntInvalidInputValueError,
    BaseTypedIntInvariantViolationError,
)
```

* `BaseTypedIntError` — root exception for library errors
* `BaseTypedIntConstraintConfigurationError` — invalid or changed constraint declaration
* `BaseTypedIntConstraintViolationError` — direct input violates a declared constraint
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
    _base_constrained_typed_int/
      __init__.py
      _base.py
      _constraints.py
    _base_typed_int.py
    _exceptions.py
    _pydantic_support.py
    py.typed
```

## Compatibility

* Python 3.10+
* CPython
* Pydantic v2 support is optional

## Notes

`BaseTypedInt` remains intentionally unconstrained. `BaseConstrainedTypedInt`
adds only deterministic integer comparisons and divisibility checks while
preserving the same callable class, runtime subtype, serialization, and static
typing model. More complex domain rules belong in the application layer.

## License

MIT
