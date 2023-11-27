from tests.test_data.account_test_data import ACCOUNTS
from datetime import datetime


def account_name_to_id(name: str) -> int:
    """Return the account ID for a given account name for the
    sake of mapping Transactions to Accounts in the test database.

    Parameters
    ----------
        name (str) : The name of the account to find the id of.

    Returns
    -------
        (int) : The ID of the account with the given name, or -1 if none
            is found.
    """
    try:
        return list(map(lambda acct: acct["name"], ACCOUNTS)).index(name) + 1
    except ValueError:
        return -1


uncategorized_one = dict(
    name="Uncategorized Test Transaction",
    description="An uncategorized test transaction for the credit card.",
    amount=123.45,
    credit_account_id=account_name_to_id("AMEX"),
    transaction_date=datetime(2023, 2, 21),
)

uncategorized_payment = dict(
    name="Uncategorized CC Payment",
    description="An uncategorized payment to the credit card.",
    amount=78.90,
    credit_account_id=account_name_to_id("Chase Savings"),
    transaction_date=datetime(2023, 2, 25),
)

uncategoried_debit_expense = dict(
    name="Uncategorized Debit Payment",
    description="Uncategorized debit payment.",
    amount=400.90,
    debit_account_Id=account_name_to_id("Chase Savings"),
    transaction_date=datetime(2023, 2, 25),
)


gas_payment = dict(
    name="Costco Gas",
    description="Costco Gas Wholesale",
    amount=67.50,
    debit_account_id=account_name_to_id("Gas for Car"),
    credit_account_id=account_name_to_id(
        "AMEX"
    ),  # Costco actually doesn't accept AMEX... awkward
    transaction_date=datetime(2023, 2, 27),
)

rent_payment = dict(
    name="March Rent",
    description="Paying the rent from savings",
    amount=1250.0,
    debit_account_id=account_name_to_id("Apartment Rent"),
    credit_account_id=account_name_to_id("Chase Savings"),
    transaction_date=datetime(2023, 3, 1),
)

credit_card_payment = dict(
    name="Credit Card Payment",
    description="Pay off credit card",
    amount=78.90,
    debit_account_id=account_name_to_id("AMEX"),
    credit_account_id=account_name_to_id("Chase Savings"),
    transaction_date=datetime(2023, 2, 24),
)

TRANSACTIONS: list[dict] = [
    uncategorized_one,
    uncategorized_payment,
    gas_payment,
    rent_payment,
    credit_card_payment,
]
