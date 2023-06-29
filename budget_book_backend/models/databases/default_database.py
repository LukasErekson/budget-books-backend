from budget_book_backend.models.account import Account
from budget_book_backend.models.account_type import AccountType
from budget_book_backend.models.db_setup import DbSetup

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from collections import namedtuple

AccType = namedtuple("AccType", ["name", "group_name"])
Acc = namedtuple("Acc", ["name", "debit_inc", "account_type_id"])


def account_type_name_to_id(name: str) -> int:
    """Return the account_type ID for a given account_type name for the
    sake of mapping Accounts to Account Types in the test database.

    Parameters
    ----------
        name (str) : The name of the account_type to find the id of.

    Returns
    -------
        (int) : The ID of the account_type with the given name, or -1 if
            none is found.
    """
    for idx, account_type in enumerate(DEFAULT_ACCOUNT_TYPES):
        if account_type.name == name:
            return idx + 1

    return -1


DEFAULT_ACCOUNT_TYPES: list[AccType] = [
    AccType(name="Checking Account", group_name="Assets"),
    AccType(name="Savings Account", group_name="Assets"),
    AccType(name="Retirement Account", group_name="Assets"),
    AccType(name="Credit Card", group_name="Liabilities"),
    AccType(name="Loan/Mortgage", group_name="Liabilities"),
    AccType(name="Recurring Expense", group_name="Expenses"),
    AccType(name="Expense", group_name="Expenses"),
    AccType(name="Seasonal Expense", group_name="Expenses"),
    AccType(name="Income", group_name="Income"),
    AccType(name="Opening Balance Equity", group_name="Equity"),
]

DEFAULT_ACCOUNTS: list[Acc] = [
    Acc(
        name="Main Checking Account",
        debit_inc=True,
        account_type_id=account_type_name_to_id("Checking Account"),
    ),
    Acc(
        name="Main Savings Account",
        debit_inc=True,
        account_type_id=account_type_name_to_id("Savings Account"),
    ),
    Acc(
        name="Credit Card",
        debit_inc=False,
        account_type_id=account_type_name_to_id("Credit Card"),
    ),
    Acc(
        name="Food & Groceries",
        debit_inc=True,
        account_type_id=account_type_name_to_id("Expense"),
    ),
    Acc(
        name="Car Expense",
        debit_inc=True,
        account_type_id=account_type_name_to_id("Expense"),
    ),
    Acc(
        name="Streaming Services",
        debit_inc=True,
        account_type_id=account_type_name_to_id("Recurring Expense"),
    ),
    Acc(
        name="Paycheck",
        debit_inc=False,
        account_type_id=account_type_name_to_id("Income"),
    ),
    Acc(
        name="Opening Balance Equity",
        debit_inc=False,
        account_type_id=account_type_name_to_id("Opening Balance Equity"),
    ),
]


def setup_default_db() -> None:
    """Create a Database and add the models (tables) to it."""
    DbSetup.engine = create_engine(
        "sqlite:///budget_book_backend/models/databases/database.db"
    )
    DbSetup.Session = sessionmaker(bind=DbSetup.engine)
    DbSetup.add_tables()

    with DbSetup.Session() as session:
        for account_type in DEFAULT_ACCOUNT_TYPES:
            session.add(
                AccountType(
                    name=account_type.name,
                    group_name=account_type.group_name,
                )
            )
        session.commit()

    with DbSetup.Session() as session:
        for account in DEFAULT_ACCOUNTS:
            session.add(
                Account(
                    name=account.name,
                    debit_inc=account.debit_inc,
                    account_type_id=account.account_type_id,
                )
            )

        session.commit()


if __name__ == "__main__":
    setup_default_db()
