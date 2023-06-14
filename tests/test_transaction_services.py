import pytest
from datetime import datetime

from budget_book_backend.models.db_setup import DbSetup
from budget_book_backend.models.transaction import Transaction
from budget_book_backend.transactions.transaction_services import (
    add_new_transactions,
    categorize_transactions,
    get_transactions_by_account,
    update_transactions,
    remove_transactions,
)
from tests.test_data.transaction_test_data import account_name_to_id
from tests.testing_utils import partial_dict_list_match


@pytest.mark.parametrize(
    ["account_ids", "categorize_type", "expected"],
    [
        (
            # Get all transactions from 'Chase Savings'
            [account_name_to_id("Chase Savings")],
            "all",
            [
                dict(
                    name="Uncategorized CC Payment",
                    amount=78.90,
                    debit_account_id="undefined",
                ),
                dict(name="March Rent", amount=1250.0),
            ],
        ),
        (
            # Get only uncategorized transactions from 'Chase Savings'
            [account_name_to_id("Chase Savings")],
            "uncategorized",
            [
                dict(
                    name="Uncategorized CC Payment",
                    amount=78.90,
                    debit_account_id="undefined",
                ),
            ],
        ),
        (
            # Get only categorized transactions from 'Chase Savings'
            [account_name_to_id("Chase Savings")],
            "categorized",
            [
                dict(
                    name="March Rent",
                    amount=1250.0,
                ),
            ],
        ),
        (
            # Get transactions from multiple accounts at once
            [account_name_to_id("Chase Savings"), account_name_to_id("AMEX")],
            "all",
            [
                dict(name="Costco Gas"),
                dict(name="Uncategorized CC Payment"),
                dict(name="Uncategorized Test Transaction"),
            ],
        ),
    ],
    ids=[
        "Get All Transactions From 'Chase Savings'",
        "Get Only Uncategorized Transactions From 'Chase Savings'",
        "Get Only Categorized Transactions from 'Chase Savings'",
        "Get Transactions from Multiple Accounts At Once",
    ],
)
def test_get_transactions_by_account(
    account_ids: list[int],
    categorize_type: str,
    expected: list[dict],
    use_test_db,
) -> None:
    """Test fetching various transactions by the account ids."""
    assert partial_dict_list_match(
        expected,
        get_transactions_by_account(
            account_ids=account_ids, categorize_type=categorize_type
        ),
    )


@pytest.mark.parametrize(
    ["transactions", "expected"],
    [
        (
            # Add 1 transaction
            [
                dict(
                    name="PyTest Transaction",
                    description="Adding a transaction during PyTest.",
                    amount=789.98,
                    debit_account_id=account_name_to_id("Chase Savings"),
                    transaction_date="2023-01-02",
                )
            ],
            dict(message="SUCCESS"),
        ),
        (
            # Add multiple transactions
            [
                dict(
                    name="PyTest Transaction",
                    description="Adding a transaction during PyTest.",
                    amount=789.98,
                    debit_account_id=account_name_to_id("Chase Savings"),
                    transaction_date="2023-01-02",
                ),
                dict(
                    name="PyTest Transaction2",
                    description="Adding a second transaction during PyTest.",
                    amount=789.98,
                    credit_account_id=account_name_to_id("Chase Savings"),
                    transaction_date="2023-01-02",
                ),
            ],
            dict(message="SUCCESS"),
        ),
        (
            # No Name In Transaction
            [
                dict(
                    description="I have no name",
                    amount=42.50,
                    debit_account_id=1,
                    transaction_date="2023-01-02",
                )
            ],
            dict(
                message="There were some errors processing the following transactions:\n0: Missing key 'name'."
            ),
        ),
        (
            # Problem transaction in middle - no amount
            [
                dict(
                    name="PyTest Transaction",
                    description="Adding a transaction during PyTest.",
                    amount=789.98,
                    debit_account_id=account_name_to_id("Chase Savings"),
                    transaction_date="2023-01-02",
                ),
                dict(
                    name="Missing amount",
                    description="I have no amount",
                    debit_account_id=1,
                    transaction_date="2023-01-02",
                ),
            ],
            dict(
                message="There were some errors processing the following transactions:\n1: Missing key 'amount'."
            ),
        ),
        # This test case is giving unexpected behavior... it's succeeding.
        # TODO: Give this another look when refactoring transaction_services.
        # (
        #     # Problem transaction - amount is an invalid string
        #     [
        #         dict(
        #             name="PyTest Transaction",
        #             description="Adding a transaction during PyTest.",
        #             amount=20.0,
        #             debit_account_id="I am a string",
        #             transaction_date="2023-01-02",
        #         ),
        #     ],
        #     dict(
        #         message="There were some errors processing the following transactions:\n1: Missing key 'amount'"
        #     ),
        # ),
    ],
    ids=[
        "Add 1 Transaction",
        "Add Multiple Transactions",
        "No Name In Transaction",
        "No Amount In One of Many Transactions",
        # "Amount Is An Invalid String"
    ],
)
def test_add_new_transactions(
    transactions: list[dict], expected: dict, use_test_db
) -> None:
    """Test adding new transactions to the database."""
    assert add_new_transactions(transactions=transactions) == expected


@pytest.mark.parametrize(
    ["transactions", "expected"],
    [
        (
            # Invalid transaction ID
            [dict(transaction_id=-1)],
            dict(
                message="There were some errors processing the following transactions:\n0: Transaction with ID -1 cannot be found."
            ),
        ),
        (
            # No transaction ID
            [dict()],
            dict(
                message="There were some errors processing the following transactions:\n0: Missing key 'transaction_id'."
            ),
        ),
        (
            # Type errors in request
            [
                dict(
                    transaction_id=1,
                    debit_or_credit="debit",
                    category_id="I should be an int",
                )
            ],
            dict(
                message="There were some errors processing the following transactions:\n0: invalid literal for int() with base 10: 'I should be an int'"
            ),
        ),
        (
            # Categorize one transaction
            [dict(transaction_id=1, debit_or_credit="debit", category_id=1)],
            dict(message="SUCCESS"),
        ),
        (
            # Categorize multiple transactions, debit and credit
            [
                dict(transaction_id=1, debit_or_credit="debit", category_id=2),
                dict(
                    transaction_id=3, debit_or_credit="credit", category_id=2
                ),
            ],
            dict(message="SUCCESS"),
        ),
    ],
    ids=[
        "Non-existant ID",
        "No Transaction ID",
        "Type Errors in Request",
        "Categorize One Transaction",
        "Categorize Multiple Transactions, Debit and Credit",
    ],
)
def test_categorize_transactions(
    transactions: list[dict], expected: dict, use_test_db
) -> None:
    """Test categorizing a list of transactions. If it categorizes the
    transactions successfully, then ensure that the database correctly
    reflects that."""
    result: dict = categorize_transactions(transactions=transactions)
    assert result == expected

    if result["message"] == "SUCCESS":
        with DbSetup.Session() as session:
            for transaction in transactions:
                current_transaction: Transaction | None = session.get(
                    Transaction, transaction["transaction_id"]
                )
                if current_transaction:
                    assert transaction["category_id"] in (
                        current_transaction.debit_account_id,
                        current_transaction.credit_account_id,
                    )
                else:
                    assert (
                        False
                    ), f"Transaction with id {transaction['transaction_id']} could not be found."


@pytest.mark.parametrize(
    ["transactions", "expected"],
    [
        (
            # Try to update a non-existent Transaction ID.
            [dict(transaction_id=-1)],
            dict(
                message="There were some errors processing the following transactions:\n0: Transaction with ID of -1 cannot be found."
            ),
        ),
        (
            # Single Transaction Update
            [dict(transaction_id=3, transaction_date="2023-02-01")],
            dict(message="SUCCESS"),
        ),
        (
            # Update multiple transactions
            [
                dict(
                    transaction_id=3,
                    name="Dinoco Gas",
                    description="Dinoco Gas",
                ),
                dict(transaction_id=4, name="April Rent"),
            ],
            dict(message="SUCCESS"),
        ),
    ],
    ids=[
        "Non-Existent ID",
        "Single Transaction Update",
        "Update Multiple Transactions",
    ],
)
def test_update_transactions(
    transactions: list[dict], expected: dict, use_test_db
) -> None:
    """Test updating a list of transactions in the database and verify
    that those changes were made in the database.
    """
    result: dict = update_transactions(transactions=transactions)
    assert result == expected

    if result["message"] == "SUCCESS":
        with DbSetup.Session() as session:
            for transaction in transactions:
                current_transaction: Transaction | None = session.get(
                    Transaction, transaction["transaction_id"]
                )
                if current_transaction is None:
                    assert False

                for updated_field in transaction.keys():
                    # ID Is already verified if it was found.
                    if "id" in updated_field:
                        continue

                    elif "date" in updated_field:
                        assert getattr(
                            current_transaction, updated_field
                        ) == datetime.fromisoformat(transaction[updated_field])

                    else:
                        assert (
                            getattr(current_transaction, updated_field)
                            == transaction[updated_field]
                        )


@pytest.mark.parametrize(
    ["transaction_ids", "expected"],
    [
        (
            # Remove 1 Transaction
            [1],
            dict(message="SUCCESS"),
        ),
        (
            # Remove 2 Transactions
            [1, 4],
            dict(message="SUCCESS"),
        ),
        (
            # Non-Existent Transciton ID
            [-1],
            dict(
                message="There were some errors processing the following transactions:\n-1: Transaction with ID of -1 cannot be found."
            ),
        ),
    ],
    ids=[
        "Remove 1 Transaction",
        "Remove 2 Transactions",
        "Non-Existent Transaction ID",
    ],
)
def test_remove_transactions(
    transaction_ids: list[int], expected: dict, use_test_db
) -> None:
    """Remove transactions based on their IDs and verify that they are
    no longer in the database.
    """
    result: dict = remove_transactions(transaction_ids=transaction_ids)

    assert result == expected

    if result["message"] == "SUCCESS":
        with DbSetup.Session() as session:
            for id in transaction_ids:
                transaction: Transaction | None = session.get(Transaction, id)

                assert transaction is None
