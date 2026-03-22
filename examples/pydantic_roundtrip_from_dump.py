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
    source_model: MetricsModel = MetricsModel.model_validate(
        {
            "primary_retry_count": 5,
            "backup_retry_count": 8,
        }
    )

    dumped_python: dict[str, object] = source_model.model_dump()
    dumped_json: str = source_model.model_dump_json()
    loaded_json_payload: dict[str, object] = json.loads(dumped_json)

    restored_from_python_dump: MetricsModel = MetricsModel.model_validate(dumped_python)
    restored_from_json_payload: MetricsModel = MetricsModel.model_validate(
        loaded_json_payload
    )

    print_section("1. source model runtime values")

    print_value_state("source_model.primary_retry_count", source_model.primary_retry_count)
    print_value_state("source_model.backup_retry_count", source_model.backup_retry_count)

    print_section("2. exported payload loses subtype")

    print(f"dumped_python                    : {dumped_python}")
    print(f"dumped_json                      : {dumped_json}")
    print(f"loaded_json_payload              : {loaded_json_payload}")

    print_value_state(
        "dumped_python['primary_retry_count']",
        dumped_python["primary_retry_count"],
    )
    print_value_state(
        "loaded_json_payload['primary_retry_count']",
        loaded_json_payload["primary_retry_count"],
    )

    print(
        f"python dump is plain int         : "
        f"{type(dumped_python['primary_retry_count']) is int}"
    )
    print(
        f"json payload is plain int        : "
        f"{type(loaded_json_payload['primary_retry_count']) is int}"
    )

    print_section("3. validation rebuilds exact subtype")

    print_value_state(
        "restored_from_python_dump.primary_retry_count",
        restored_from_python_dump.primary_retry_count,
    )
    print_value_state(
        "restored_from_json_payload.primary_retry_count",
        restored_from_json_payload.primary_retry_count,
    )

    print(
        f"restored from python dump        : "
        f"{type(restored_from_python_dump.primary_retry_count) is RetryCount}"
    )
    print(
        f"restored from json payload       : "
        f"{type(restored_from_json_payload.primary_retry_count) is RetryCount}"
    )

    print_section("4. final verdict")

    print("dump/export boundary             : subtype is flattened to plain int")
    print("validation boundary              : subtype is reconstructed correctly")
    print(
        f"original model unchanged         : "
        f"{type(source_model.primary_retry_count) is RetryCount}"
    )


if __name__ == "__main__":
    main()