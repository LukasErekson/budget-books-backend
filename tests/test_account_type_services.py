from typing import Optional

import pytest
from sqlalchemy import Select, select

from budget_book_backend.account_types.account_type_services import (
    create_account_type,
    get_account_types,
)
from budget_book_backend.models.account_type import AccountType
from budget_book_backend.models.db_setup import DbSetup

from .test_data.account_type_test_data import (
    ACCOUNT_TYPES,
    EXPENSES,
    LIABILITIES,
)


@pytest.mark.parametrize(
    ["group", "expected", "fail_message"],
    [
        ("all", ACCOUNT_TYPES, "'all' failed to return all types."),
        (
            "Liabilities",
            LIABILITIES,
            "'Liabilities' not returned with argument.",
        ),
        (
            "Expenses",
            EXPENSES,
            "'Expenses' not returned with argument.",
        ),
        (
            "Not a real Account Type group",
            [],
            "Invalid group does not return an empty list.",
        ),
    ],
)
def test_get_account_types_happy(
    group: str, expected: list[dict], fail_message: str, use_test_db
) -> None:
    """Test that get_account_types returns the right list of
    account_type dicitonaries given various group names.
    """
    assert get_account_types(group) == expected, fail_message


def test_get_account_types_bad_group(use_test_db) -> None:
    """Test that a specific error message is given if the group passed
    in is not in the database.
    """
    assert get_account_types("not_a_type") == []


@pytest.mark.parametrize(
    ["name", "group", "expected"],
    [
        (
            "A New Checking Account",
            "Assets",
            dict(message="SUCCESS", account_name="A New Checking Account"),
        ),
        (
            "Grocery Shopping",
            "Expenses",
            dict(message="SUCCESS", account_name="Grocery Shopping"),
        ),
    ],
)
def test_create_account_type_happy(
    name: str, group: str, expected: dict, use_test_db
) -> None:
    """Test various happy paths for create_account_type with various
    parameters.
    """
    # Ensure the correct return value
    assert create_account_type(name, group) == expected

    with DbSetup.Session() as session:
        statement: Select[tuple[AccountType]] = select(AccountType).filter_by(
            name=name, group=group
        )
        new_account_type: Optional[AccountType] = session.scalar(statement)

        # Ensure it's been added/committed to the Database
        assert (
            new_account_type is not None
        ), f"failed to add {name} to database."

        # Ensure that it has a valid ID
        assert new_account_type.id


def test_create_account_type_no_group(use_test_db) -> None:
    """Test that create_account_type without a group name defaults the
    group to 'Misc'.
    """
    expected_response: dict = create_account_type("Subscription")

    assert expected_response == dict(
        message="SUCCESS", account_name="Subscription"
    )

    with DbSetup.Session() as session:
        statement: Select[tuple[AccountType]] = select(AccountType).filter_by(
            name="Subscription", group="Misc."
        )
        new_account_type: Optional[AccountType] = session.scalar(statement)

        # Ensure it's been added/committed to the Database
        assert (
            new_account_type is not None
        ), "failed to add Subscription to database."

        # Ensure that it has a valid ID
        assert new_account_type.id


def test_create_account_type_not_unique(use_test_db) -> None:
    """Test that create_account_type returns a specific sqlalchemy error
    message when the uniqueness constraint is violated.
    """
    expected_response: dict = create_account_type("Checking Account", "Assets")

    assert (
        expected_response["message"]
        == "There was a problem posting the new account type."
    )

    assert expected_response["account_name"] == "Checking Account"

    assert "error" in expected_response
    assert "UNIQUE constraint failed" in expected_response["error"]


def test_create_account_type_null_name(use_test_db) -> None:
    """Test that create_account_type returns a dict with a specific
    error message when the account_type_name was empty.
    """
    expected_response: dict = create_account_type("", "Assets")

    assert (
        expected_response["message"]
        == "There was a problem posting the new account type."
    )

    assert expected_response["account_name"] == ""

    assert "error" in expected_response
    assert (
        "Cannot create an account type without a name."
        == expected_response["error"]
    )
