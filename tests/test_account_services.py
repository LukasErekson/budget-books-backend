from datetime import datetime

import pytest

from budget_book_backend.accounts.account_services import (
    account_balances,
    add_new_account_to_db,
    get_accounts_by_type,
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
        (("Gas",), [{"name": "Gas for Car", "balance": 67.50}]),
        (
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
            # Before any transactions cleared, balance is 0
            datetime(2022, 1, 1),
            datetime(2022, 12, 31),
            [
                {"name": "AMEX", "balance": 0.0},
                {"name": "Chase Savings", "balance": 0.0},
            ],
        ),
        (
            # After a CC charge but before rent
            datetime(2023, 1, 1),
            datetime(2023, 2, 27),
            [
                {"name": "AMEX", "balance": 67.50},
                {"name": "Chase Savings", "balance": 0.0},
            ],
        ),
        (
            # Beginning after a CC charge and after Rent
            datetime(2023, 3, 1),
            datetime(2023, 3, 27),
            [
                {"name": "AMEX", "balance": 0.0},
                {"name": "Chase Savings", "balance": -1250.0},
            ],
        ),
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
            # Create a new account type if id is -1
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
)
def test_add_new_account_to_db(
    name: str,
    account_type_id: int,
    account_type_label: str,
    debit_inc: bool,
    expected: dict,
    use_test_db,
):
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
)
def test_account_balances(account_ids: list[int], expected: dict, use_test_db):
    """Test getting the current account balances for given account IDS."""
    actual_return: dict = account_balances(account_ids=account_ids)

    # Relevant account information is returned
    assert partial_dict_match(expected, actual_return)

    # Extra accounts aren't being returned
    assert len(expected) == len(actual_return)
