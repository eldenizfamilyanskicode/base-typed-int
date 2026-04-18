from __future__ import annotations

import json

from pydantic import BaseModel

from base_typed_int import BaseTypedInt


class RetryCount(BaseTypedInt):
    pass


class MetricsModel(BaseModel):
    primary_retry_count: RetryCount
    backup_retry_count: RetryCount


def print_section(title: str) -> None:
    separator: str = "=" * len(title)
    print()
    print(separator)
    print(title)
    print(separator)


def print_value_state(label: str, value: object) -> None:
    print(f"{label}:")
    print(f"  repr         : {value!r}")
    print(f"  runtime type : {type(value).__name__}")
    print()


def main() -> None:
    metrics_model: MetricsModel = MetricsModel.model_validate(
        {
            "primary_retry_count": 5,
            "backup_retry_count": 8,
        }
    )

    dumped_python: dict[str, object] = metrics_model.model_dump()
    dumped_json: str = metrics_model.model_dump_json()
    loaded_from_json: dict[str, object] = json.loads(dumped_json)

    primary_retry_count_from_dump: object = dumped_python["primary_retry_count"]
    backup_retry_count_from_dump: object = dumped_python["backup_retry_count"]

    primary_retry_count_from_json_payload: object = loaded_from_json[
        "primary_retry_count"
    ]
    backup_retry_count_from_json_payload: object = loaded_from_json[
        "backup_retry_count"
    ]

    print_section("1. runtime values inside pydantic model")

    print_value_state(
        "metrics_model.primary_retry_count", metrics_model.primary_retry_count
    )
    print_value_state(
        "metrics_model.backup_retry_count", metrics_model.backup_retry_count
    )

    print(
        f"primary_retry_count exact subtype kept: "
        f"{type(metrics_model.primary_retry_count) is RetryCount}"
    )
    print(
        f"backup_retry_count exact subtype kept : "
        f"{type(metrics_model.backup_retry_count) is RetryCount}"
    )

    print_section("2. python dump")

    print(f"model_dump() result              : {dumped_python}")
    print_value_state("primary_retry_count_from_dump", primary_retry_count_from_dump)
    print_value_state("backup_retry_count_from_dump", backup_retry_count_from_dump)

    print(
        f"primary_retry_count flattened to int: "
        f"{type(primary_retry_count_from_dump) is int}"
    )
    print(
        f"backup_retry_count flattened to int : "
        f"{type(backup_retry_count_from_dump) is int}"
    )

    print_section("3. json dump")

    print(f"model_dump_json() result         : {dumped_json}")
    print(f"json.loads(...) result           : {loaded_from_json}")

    print_value_state(
        "primary_retry_count_from_json_payload",
        primary_retry_count_from_json_payload,
    )
    print_value_state(
        "backup_retry_count_from_json_payload",
        backup_retry_count_from_json_payload,
    )

    print(
        f"json payload contains plain int  : "
        f"{type(primary_retry_count_from_json_payload) is int}"
    )
    print(
        f"json payload contains plain int  : "
        f"{type(backup_retry_count_from_json_payload) is int}"
    )

    print_section("4. final verdict")

    print("inside model                     : exact subtype is preserved")
    print("after model_dump()               : exported payload is plain int")
    print("after model_dump_json()          : exported payload is plain int")
    print(
        f"original model still keeps subtype: "
        f"{type(metrics_model.primary_retry_count) is RetryCount}"
    )


if __name__ == "__main__":
    main()
