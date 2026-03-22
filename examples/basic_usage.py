from __future__ import annotations

from base_typed_int import BaseTypedInt


class UserAge(BaseTypedInt):
    pass


class Account:
    def __init__(self, user_age: UserAge) -> None:
        self.user_age: UserAge = user_age


def print_section(title: str) -> None:
    separator: str = "=" * len(title)
    print()
    print(separator)
    print(title)
    print(separator)


def print_value_state(label: str, value: object) -> None:
    print(f"{label}:")
    print(f"  repr                  : {value!r}")
    print(f"  runtime type          : {type(value).__name__}")
    print(f"  isinstance(value, int): {isinstance(value, int)}")
    print()


def print_runtime_membership(label: str, value: object) -> None:
    print(f"isinstance({label}, UserAge)    : {isinstance(value, UserAge)}")
    print(f"isinstance({label}, int)        : {isinstance(value, int)}")


def demonstrate_direct_runtime_identity() -> None:
    print_section("1. direct construction")

    user_age: UserAge = UserAge(18)

    print_value_state("constructed value", user_age)
    print(f"value == 18                      : {user_age == 18}")
    print(f"type(user_age) is UserAge        : {type(user_age) is UserAge}")
    print_runtime_membership("user_age", user_age)


def demonstrate_container_and_attribute_behavior() -> None:
    print_section("2. containers and class attributes")

    source_user_age: UserAge = UserAge(18)

    user_age_list: list[UserAge] = [source_user_age]
    user_age_by_field_name: dict[str, UserAge] = {
        "user_age": source_user_age,
    }
    values_by_user_age: dict[int, str] = {
        source_user_age: "present",
    }
    account: Account = Account(user_age=source_user_age)

    retrieved_from_list: UserAge = user_age_list[0]
    retrieved_from_dict_value: UserAge = user_age_by_field_name["user_age"]
    retrieved_from_attribute: UserAge = account.user_age
    retrieved_by_typed_key: str = values_by_user_age[source_user_age]
    retrieved_by_plain_int_key: str = values_by_user_age[18]

    stored_keys: tuple[int, ...] = tuple(values_by_user_age.keys())
    stored_key_object: int = stored_keys[0]

    print_value_state("source_user_age", source_user_age)
    print_value_state("retrieved_from_list", retrieved_from_list)
    print_value_state("retrieved_from_dict_value", retrieved_from_dict_value)
    print_value_state("retrieved_from_attribute", retrieved_from_attribute)
    print_value_state("stored_key_object", stored_key_object)

    print(
        f"list keeps same object           : {retrieved_from_list is source_user_age}"
    )
    print(
        f"dict value keeps same object     : "
        f"{retrieved_from_dict_value is source_user_age}"
    )
    print(
        f"class attribute keeps same object: "
        f"{retrieved_from_attribute is source_user_age}"
    )
    print(
        f"dict key object is same object   : {stored_key_object is source_user_age}"
    )
    print(f"typed key lookup works           : {retrieved_by_typed_key == 'present'}")
    print(
        f"plain int key lookup works       : "
        f"{retrieved_by_plain_int_key == 'present'}"
    )
    print(f"stored key exact subtype kept    : {type(stored_key_object) is UserAge}")


def demonstrate_normal_integer_operations() -> None:
    print_section("3. normal integer operations")

    user_age: UserAge = UserAge(18)

    incremented_value: int = user_age + 1
    multiplied_value: int = user_age * 2
    subtracted_value: int = user_age - 3

    print_value_state("user_age", user_age)
    print_value_state("incremented_value", incremented_value)
    print_value_state("multiplied_value", multiplied_value)
    print_value_state("subtracted_value", subtracted_value)

    print(f"type(incremented_value) is int   : {type(incremented_value) is int}")
    print(f"type(multiplied_value) is int    : {type(multiplied_value) is int}")
    print(f"type(subtracted_value) is int    : {type(subtracted_value) is int}")
    print("verdict                          : normal int operations return plain int")


def main() -> None:
    demonstrate_direct_runtime_identity()
    demonstrate_container_and_attribute_behavior()
    demonstrate_normal_integer_operations()


if __name__ == "__main__":
    main()