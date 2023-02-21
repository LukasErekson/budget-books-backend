from datetime import datetime
import pandas as pd
from typing import Mapping
from models.db_setup import DbSetup
from utils import dict_to_json
from models.transaction import Transaction


def get_transactions_by_account(
    account_ids: list[int], categorize_type: str = "all"
) -> list[dict]:
    """Return all the transactions that are associated with the
    account_id OR all of the given transaction categories.

    Parameters
    ----------
        account_ids (list of ints) : The account/category ID's to fetch
            the transactions from.
        categorize_type (str) : Whether to only fetch uncategorized,
            categorized, or all kinds of transactions.

    Returns
    -------
        (list of dicts) : List of dictionary transaction objects
            matching the given query.
    """
    df: pd.DataFrame = pd.DataFrame()

    if len(account_ids) == 1:
        df = pd.read_sql_query(
            f"""SELECT * FROM transactions
                WHERE debit_account_id = {account_ids[0]}
                    OR credit_account_id = {account_ids[0]}""",
            DbSetup.engine,
        )

    else:
        df = pd.read_sql_query(
            f"""SELECT * FROM transactions
                WHERE debit_account_id IN {tuple(account_ids)}
                    OR credit_account_id IN {tuple(account_ids)}""",
            DbSetup.engine,
        )

    if categorize_type == "uncategorized":
        # Only accept those that are uncategorized
        df = df[
            (
                pd.isna(df["debit_account_id"])
                | (pd.isna(df["credit_account_id"]))
            )
        ]

    elif categorize_type == "categorized":
        # Only accept those that are categorized
        df = df[
            (
                pd.notna(df["debit_account_id"])
                & (pd.notna(df["credit_account_id"]))
            )
        ]

    # Else, assume all the transactions are wanted.
    df.fillna("undefined", inplace=True)

    return dict_to_json(df.to_dict(), df.index)


def add_new_transactions(transactions: list[Mapping]) -> dict:
    """Add new transaction(s) with the given information.

    Parameters
    ----------
        transactions (list[Mapping]) : List of transaction data to add
            to the Transactions table.

    Returns
    -------
        (dict) : Dictionary containing a message about whether or not
            there was a problem with one or more transacations.
    """

    with DbSetup.Session() as session:
        new_transactions: list[Transaction] = []
        problem_transactions: list[tuple] = []

        for i, trxn in enumerate(transactions):
            try:
                new_transactions.append(
                    Transaction(
                        name=trxn["name"],
                        description=trxn["description"],
                        amount=trxn["amount"],
                        debit_account_id=trxn.get("debit_account_id"),
                        credit_account_id=trxn.get("credit_account_id"),
                        transaction_date=datetime.fromisoformat(
                            trxn["transaction_date"]
                        ),
                        date_entered=datetime.now(),
                    )
                )
            except Exception as e:
                problem_transactions.append((i, str(e)))

        session.add_all(new_transactions)
        session.commit()

    message: str = "SUCCESS"

    if len(problem_transactions) != 0:
        message = (
            "There were some errors processing the following transactions:"
        )

        for idx, problem in problem_transactions:
            message += f"\n{idx}: {problem}"

    return dict(message=message)


def categorize_transactions(transactions: list[Mapping]) -> dict:
    """Categorize the given transaction(s).

    Parameters
    ---------
        transactions (list[Mapping]) : List of transaction data to adjust
            in the database.

    Returns
    -------
        (dict) : Dictionary containing a message about whether or not
            there was a problem with one or more transacations.
    """
    problem_transactions: list[tuple] = []

    with DbSetup.Session() as session:

        for i, trxn in enumerate(transactions):
            try:
                transaction: Transaction = (
                    session.query(Transaction)
                    .filter(Transaction.id == trxn["transaction_id"])
                    .scalar()
                )

                if trxn["debit_or_credit"] == "debit":
                    transaction.debit_account_id = int(trxn["category_id"])

                else:
                    transaction.credit_account_id = int(trxn["category_id"])

                session.commit()
            except Exception as e:
                problem_transactions.append((i, str(e)))

    message: str = "SUCCESS"

    if len(problem_transactions) != 0:
        message = (
            "There were some errors processing the following transactions:"
        )

        for idx, problem in problem_transactions:
            message += f"\n{idx}: {problem}"

    return dict(message=message)


def update_transactions(transactions: list[Mapping]) -> dict:
    """Change existing transaction(s) to have new given values.

    Parameters
    ----------
        transactions (list[Mapping]) : The list of transactions to
            update in the database.

    Returns
    -------
        (dict) : Dictionary containing a status message of the udpates.
    """
    problem_transactions: list[tuple] = []

    with DbSetup.Session() as session:

        for i, trxn in enumerate(transactions):
            try:
                transaction: Transaction = (
                    session.query(Transaction)
                    .filter(Transaction.id == trxn["id"])
                    .scalar()
                )

                transaction.name = trxn.get("name") or transaction.name
                transaction.description = (
                    trxn.get("description") or transaction.description
                )
                transaction.amount = trxn.get("amount") or transaction.amount
                transaction.debit_account_id = (
                    trxn.get("debit_account_id")
                    or transaction.debit_account_id
                )
                transaction.credit_account_id = (
                    trxn.get("credit_account_id")
                    or transaction.credit_account_id
                )
                transaction.transaction_date = (
                    datetime.fromisoformat(trxn.get("transaction_date", None))
                    or transaction.transaction_date
                )
                transaction.date_entered = datetime.now()

                session.commit()

            except Exception as e:
                problem_transactions.append((i, str(e)))

    message: str = "SUCCESS"

    if len(problem_transactions) != 0:
        message = (
            "There were some errors processing the following transactions:"
        )

        for idx, problem in problem_transactions:
            message += f"\n{idx}: {problem}"

    return dict(message=message)


def remove_transactions(transaction_ids: list[int]) -> dict:
    """Removes the transactions with the given IDs.

    Parameters
    ----------
        transaction_ids (list[int]) : The IDs of the transactions to
            remove from the database.

    Returns
    -------
        (dict) : Dictionary containing the status message for the
            deleted transactions.
    """
    problem_transactions: list[tuple] = []

    with DbSetup.Session() as session:

        for transaction_id in transaction_ids:
            try:
                transaction: Transaction = (
                    session.query(Transaction)
                    .filter(Transaction.id == transaction_id)
                    .one()
                )

                session.delete(transaction)

                session.commit()
            except Exception as e:
                problem_transactions.append((transaction_id, str(e)))

    message: str = "SUCCESS"

    if len(problem_transactions) != 0:
        message = (
            "There were some errors processing the following transactions:"
        )

        for idx, problem in problem_transactions:
            message += f"\n{idx}: {problem}"

    return dict(message=message)
