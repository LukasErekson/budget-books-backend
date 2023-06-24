from datetime import datetime

import pytest

from budget_book_backend.accounts.account_services import (
    account_balances,
    add_new_account_to_db,
    get_accounts_by_type,
    update_account_info,
    delete_account,
)
from budget_book_backend.models.account import Account
from budget_book_backend.models.db_setup import DbSetup
from tests.testing_utils import partial_dict_list_match, partial_dict_match
from tests.test_data.transaction_test_data import account_name_to_id
from tests.test_data.account_test_data import account_type_name_to_id, ACCOUNTS


@pytest.mark.parametrize(
    ["types", "expected"],
    [
        (
            # Get 'Checking Account', 'Savings Account', and 'Credit Card' Accounts
            ("Checking Account", "Savings Account", "Credit Card"),
            [
                {
                    "name": "AMEX",
                    "balance": 67.50,
                    "uncategorized_transactions": 1,
                    "account_type": "Credit Card",
                },
                {
                    "name": "Chase Savings",
                    "balance": -1250.0,
                    "account_type": "Savings Account",
                },
            ],
        ),
        (
            # Get 1 Expense Account
            ("Gas",),
            [{"name": "Gas for Car", "balance": 67.50}],
        ),
        (
            # Get 2 Expense Accounts
            ("Rent", "Gas"),
            [
                {
                    "name": "Apartment Rent",
                    "balance": 1250.0,
                    "account_type": "Rent",
                },
                {"name": "Gas for Car", "balance": 67.50},
            ],
        ),
    ],
    ids=[
        "Get 'Checking Account', 'Savings Account', and 'Credit Card' Accounts",
        "Get 1 Expense Account",
        "Get 2 Expense Accoutns",
    ],
)
def test_get_accounts_by_type_different_types(
    types: tuple[str, ...], expected: list[dict], use_test_db
) -> None:
    """Test that get_accounts_by_type returns various account details
    when given different type parameters."""
    actual_return: list[dict] = get_accounts_by_type(
        types=types,
        balance_start_date=datetime(1, 1, 1),
        balance_end_date=datetime.now(),
    )

    # Relevant account information is returned
    assert partial_dict_list_match(expected, actual_return)

    # Extra accounts aren't being returned
    assert len(expected) == len(actual_return)


@pytest.mark.parametrize(
    ["start_date", "end_date", "expected"],
    [
        (
            # Before Any Transactions Cleared ($0.00 Balances)
            datetime(2022, 1, 1),
            datetime(2022, 12, 31),
            [
                {"name": "AMEX", "balance": 0.0},
                {"name": "Chase Savings", "balance": 0.0},
            ],
        ),
        (
            # In Between Cleared Transactions
            # After a CC charge but before rent
            datetime(2023, 1, 1),
            datetime(2023, 2, 27),
            [
                {"name": "AMEX", "balance": 67.50},
                {"name": "Chase Savings", "balance": 0.0},
            ],
        ),
        (
            # After Multiple Transactions Cleared
            # Beginning after a CC charge and after Rent
            datetime(2023, 3, 1),
            datetime(2023, 3, 27),
            [
                {"name": "AMEX", "balance": 0.0},
                {"name": "Chase Savings", "balance": -1250.0},
            ],
        ),
    ],
    ids=[
        "Before Any Transactions Cleared ($0.00 Balances)",
        "In Between Cleared Transactions",
        "After Multiple Transactions Cleared",
    ],
)
def test_get_accounts_by_type_different_dates(
    start_date: datetime, end_date: datetime, expected: list[dict], use_test_db
) -> None:
    """Test that different dates correctly yield the balances expected."""
    actual_return: list[dict] = get_accounts_by_type(
        types=("Credit Card", "Savings Account"),
        balance_start_date=start_date,
        balance_end_date=end_date,
    )

    # Relevant account information is returned
    assert partial_dict_list_match(expected, actual_return)

    # Extra accounts aren't being returned
    assert len(expected) == len(actual_return)


@pytest.mark.parametrize(
    ("name", "account_type_id", "account_type_label", "debit_inc", "expected"),
    [
        (
            # Add New Credit Card
            "BofA CC",
            account_type_name_to_id("Credit Card"),
            "Credit Card",
            False,
            dict(
                message="SUCCESS",
                account_name="BofA CC",
                account_id=len(ACCOUNTS) + 1,
            ),
        ),
        (
            # Create A New Account Type if ID is -1
            "New Misc Expense",
            -1,
            "New Account Type",
            True,
            dict(
                message="SUCCESS",
                account_name="New Misc Expense",
                account_id=len(ACCOUNTS) + 1,
            ),
        ),
    ],
    ids=["Add New Credit Card", "Create A New Account Type if ID is -1"],
)
def test_add_new_account_to_db(
    name: str,
    account_type_id: int,
    account_type_label: str,
    debit_inc: bool,
    expected: dict,
    use_test_db,
) -> None:
    """Test adding new accounts to the database and getting a positive
    response.
    """
    response: dict = add_new_account_to_db(
        name=name,
        account_type_id=account_type_id,
        account_type_label=account_type_label,
        debit_inc=debit_inc,
    )

    assert response == expected

    # Ensure account was added to the database
    with DbSetup.Session() as session:
        assert len(session.query(Account).all()) == 5
        assert session.query(Account).filter_by(name=name).scalar()


@pytest.mark.parametrize(
    ["account_ids", "expected"],
    [
        (
            # Get 2 Account Balances
            [
                account_name_to_id(acct_name)
                for acct_name in ["AMEX", "Chase Savings"]
            ],
            {
                account_name_to_id("Chase Savings"): -1250.0,
                account_name_to_id("AMEX"): 67.50,
            },
        ),
        (
            # Get 4 Account Balances
            [
                account_name_to_id(acct_name)
                for acct_name in [
                    "AMEX",
                    "Chase Savings",
                    "Gas for Car",
                    "Apartment Rent",
                ]
            ],
            {
                account_name_to_id("Chase Savings"): -1250.0,
                account_name_to_id("AMEX"): 67.50,
                account_name_to_id("Gas for Car"): 67.50,
                account_name_to_id("Apartment Rent"): 1250.0,
            },
        ),
    ],
    ids=["Get 2 Account Balances", "Get 4 Account Balances"],
)
def test_account_balances(
    account_ids: list[int], expected: dict, use_test_db
) -> None:
    """Test getting the current account balances for given account IDS."""
    actual_return: dict = account_balances(account_ids=account_ids)

    # Relevant account information is returned
    assert partial_dict_match(expected, actual_return)

    # Extra accounts aren't being returned
    assert len(expected) == len(actual_return)


@pytest.mark.parametrize(
    ["edit_account", "expected"],
    [
        (
            # Valid Account Update
            dict(
                id=2,
                name="Edited Account Name",
                account_type_id=1,
                debit_inc=True,
            ),
            dict(message="SUCCESS"),
        ),
        (
            # Empty Account Name
            dict(id=3, name="", account_type_id=1, debit_inc=False),
            dict(message="ERROR", error="Account name cannot be blank."),
        ),
    ],
    ids=["Valid Account Update", "Empty Account Name"],
)
def test_update_account_info(
    edit_account: dict, expected: dict, use_test_db
) -> None:
    """Test udpating several transactions in the Database."""
    response: dict = update_account_info(edit_account)
    assert response == expected

    # Skip Database verfication if there was an error
    if "error" in response:
        return

    with DbSetup.Session() as session:
        updated_account: Account | None = session.get(
            Account, edit_account["id"]
        )

        for key in edit_account.keys():
            assert updated_account.__getattribute__(key) == edit_account[key]


@pytest.mark.parametrize(
    ["delete_account_id", "expected"],
    [
        # Successful Deletion of Existing Account
        (1, dict(message="SUCCESS")),
    ],
    ids=[
        "Successful Deletion of Existing Account",
    ],
)
def test_delete_account(delete_account_id: int, expected: dict, use_test_db):
    """Test deleting a single transaction at a time."""
    result: dict = delete_account(delete_account_id=delete_account_id)

    assert result == expected

    if result["message"] == "SUCCESS":
        with DbSetup.Session() as session:
            deleted_account: Account | None = session.get(
                Account, delete_account_id
            )

            assert deleted_account is None
