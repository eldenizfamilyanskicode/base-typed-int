from __future__ import annotations

from pydantic import BaseModel, ValidationError

from base_typed_int import BaseConstrainedTypedInt


class RequestExecutionLeaseTtlMilliseconds(BaseConstrainedTypedInt):
    ge = 1_000
    le = 3_600_000


class LeaseModel(BaseModel):
    lease_ttl: RequestExecutionLeaseTtlMilliseconds


def main() -> None:
    lease_model = LeaseModel.model_validate({"lease_ttl": 30_000})

    print(f"runtime value: {lease_model.lease_ttl!r}")
    print(f"runtime type: {type(lease_model.lease_ttl).__name__}")
    print(f"plain dump: {lease_model.model_dump()}")
    print(f"JSON Schema: {LeaseModel.model_json_schema()}")

    try:
        LeaseModel.model_validate({"lease_ttl": 500})
    except ValidationError as validation_error:
        print(f"rejected: {validation_error.errors()[0]['type']}")


if __name__ == "__main__":
    main()
