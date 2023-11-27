from datetime import datetime, timedelta
import pandas as pd

from budget_book_backend.models.db_setup import DbSetup
from budget_book_backend.models.transaction import Transaction
from budget_book_backend.utils import dict_to_json
from sqlalchemy import text, select
import sqlalchemy as sqla


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
            text(
                f"""SELECT * FROM transactions
                WHERE debit_account_id = {account_ids[0]}
                    OR credit_account_id = {account_ids[0]}"""
            ),
            DbSetup.engine.connect(),
        )

    else:
        df = pd.read_sql_query(
            text(
                f"""SELECT * FROM transactions
                WHERE debit_account_id IN {tuple(account_ids)}
                    OR credit_account_id IN {tuple(account_ids)}"""
            ),
            DbSetup.engine.connect(),
        )

    if categorize_type == "uncategorized":
        # Only accept those that are uncategorized
        df = df[(pd.isna(df["debit_account_id"]) | (pd.isna(df["credit_account_id"])))]

    elif categorize_type == "categorized":
        # Only accept those that are categorized
        df = df[
            (pd.notna(df["debit_account_id"]) & (pd.notna(df["credit_account_id"])))
        ]

    # Else, assume all the transactions are wanted.
    df.fillna("undefined", inplace=True)

    return dict_to_json(df.to_dict(), df.index)


def add_new_transactions(transactions: list[dict]) -> dict:
    """Add new transaction(s) with the given information.

    Parameters
    ----------
        transactions (list[dict]) : List of transaction data to add
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

            except KeyError as key_err:
                problem_transactions.append((i, f"Missing key {str(key_err)}."))
            except Exception as e:
                problem_transactions.append((i, str(e)))

        session.add_all(new_transactions)
        session.commit()

    message: str = "SUCCESS"

    if len(problem_transactions) != 0:
        message = "There were some errors processing the following transactions:"

        for idx, problem in problem_transactions:
            message += f"\n{idx}: {problem}"

    return dict(message=message)


def categorize_transactions(transactions: list[dict]) -> dict:
    """Categorize the given transaction(s).

    Parameters
    ---------
        transactions (list[dict]) : List of transaction data to adjust
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
                transaction_id: int = trxn["transaction_id"]
                transaction: Transaction | None = session.get(
                    Transaction, transaction_id
                )

                if transaction is None:
                    raise Exception(
                        f"Transaction with ID {transaction_id} cannot be found."
                    )

                if trxn["debit_or_credit"] == "debit":
                    transaction.debit_account_id = int(trxn["category_id"])

                else:
                    transaction.credit_account_id = int(trxn["category_id"])

                session.commit()

            except KeyError as key_err:
                problem_transactions.append((i, f"Missing key {str(key_err)}."))

            except Exception as e:
                problem_transactions.append((i, str(e)))

    message: str = "SUCCESS"

    if len(problem_transactions) != 0:
        message = "There were some errors processing the following transactions:"

        for idx, problem in problem_transactions:
            message += f"\n{idx}: {problem}"

    return dict(message=message)


def update_transactions(transactions: list[dict]) -> dict:
    """Change existing transaction(s) to have new given values.

    Parameters
    ----------
        transactions (list[dict]) : The list of transactions to
            update in the database.

    Returns
    -------
        (dict) : Dictionary containing a status message of the udpates.
    """
    problem_transactions: list[tuple] = []

    with DbSetup.Session() as session:
        for i, trxn in enumerate(transactions):
            try:
                transaction_id: int = trxn["transaction_id"]
                transaction: Transaction | None = session.get(
                    Transaction, transaction_id
                )

                if transaction is None:
                    raise Exception(
                        f"Transaction with ID of {transaction_id} cannot be found."
                    )

                transaction.name = trxn.get("name", transaction.name)

                transaction.description = trxn.get(
                    "description", transaction.description
                )

                transaction.amount = trxn.get("amount", transaction.amount)

                sent_debit_account_id = trxn.get(
                    "debit_account_id", transaction.debit_account_id
                )
                if sent_debit_account_id != "undefined":
                    transaction.debit_account_id = sent_debit_account_id

                sent_credit_account_id = trxn.get(
                    "credit_account_id", transaction.credit_account_id
                )
                if sent_credit_account_id != "undefined":
                    transaction.credit_account_id = sent_credit_account_id

                transaction_date: str | None = trxn.get("transaction_date")

                if transaction_date:
                    transaction.transaction_date = datetime.fromisoformat(  # type: ignore
                        transaction_date
                    )
                else:
                    transaction.transaction_date = transaction.transaction_date

                transaction.date_entered = datetime.now()  # type: ignore

                session.commit()

            except Exception as e:
                problem_transactions.append((i, str(e)))

    message: str = "SUCCESS"

    if len(problem_transactions) != 0:
        message = "There were some errors processing the following transactions:"

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
                transaction: Transaction | None = session.get(
                    Transaction, transaction_id
                )

                if transaction is None:
                    raise Exception(
                        f"Transaction with ID of {transaction_id} cannot be found."
                    )

                session.delete(transaction)

                session.commit()
            except Exception as e:
                problem_transactions.append((transaction_id, str(e)))

    message: str = "SUCCESS"

    if len(problem_transactions) != 0:
        message = "There were some errors processing the following transactions:"

        for idx, problem in problem_transactions:
            message += f"\n{idx}: {problem}"

    return dict(message=message)


def find_matches(
    transaction_id: int, uncategorized_only: bool = True, day_threshold: int = 2
) -> dict:
    """Find the potential matches for a given transaction. This includes
    finding the corresponding transaction across 2 accounts.
    For example,
        Checking Account credit -> Payment to Credit card
    would also show up as
        Credit Card debit -> Payment from Checking

    Parameters
    ----------
        transaction_id (int) : The transaction ID to find the matches
            or duplicates of.
        uncategorized_only (bool) : Optional. Whether or not to consider
            only the uncategorized transactions.
        day_threshold (int) : Optional. How many days to consider when
            trying to find similar transaction dates.

    Returns
    -------
        (dict) : Dictionary containing a message whether matches were
            found and a list of transaction IDs that match.
    """
    with DbSetup.Session() as session:
        transaction: Transaction | None = session.get(Transaction, transaction_id)

        if transaction is None:
            raise Exception(f"Transaciton with id {transaction_id} could not be found.")

        t_date: datetime = transaction.transaction_date  # type: ignore

        if uncategorized_only:
            matching_query = select(Transaction.id).where(
                Transaction.amount == transaction.amount,
                Transaction.id != transaction.id,
                sqla.or_(
                    Transaction.credit_account_id == None,
                    Transaction.debit_account_id == None,
                ),
                Transaction.transaction_date.between(
                    t_date - timedelta(days=day_threshold),
                    t_date + timedelta(days=day_threshold),
                ),
            )
        else:
            matching_query = select(Transaction.id).where(
                Transaction.amount == transaction.amount,
                Transaction.id != transaction.id,
                Transaction.transaction_date.between(
                    t_date - timedelta(days=day_threshold),
                    t_date + timedelta(days=day_threshold),
                ),
            )

        matching_transaction_ids = session.execute(matching_query).scalars().all()

    if not matching_transaction_ids:
        return dict(message="No matching transactions found", transaction_ids=[])

    return dict(
        message="Matching transactions found!", transaction_ids=matching_transaction_ids
    )
