import pandas as pd
from datetime import datetime

from utils import dict_to_json

from models.account import Account
from models.account_type import AccountType
from models.db_setup import DbSetup


def get_accounts_by_type(
    types: list[str], balance_start_date: datetime, balance_end_date: datetime
) -> list[dict]:
    """Select and return all of the accounts within the types list with
    balances calculated between the start date and end date.

    Parameters
    ----------
        types (list[str]) : The type of accounts to fetch. For example,
            "bank", "category", or "all".
        balance_start_date (datetime) : The earliest date to use when
            calculating the balance of the returned accounts.
        balance_end_date (datetime) : The latest date to use when
            calculating the balance of the returned accounts.

    Returns
    -------
        (list[dict]) : The list of the accounts with their id, name,
            balance (as of balance_end_date), and whether they are a
            debit increase account or not. This list of dicts makes it
            simple to convert to a dict that is JSON serializable.

    """
    sql_statement: str = """SELECT * FROM accounts"""

    if isinstance(types, str):
        if types != "all":
            sql_statement += f""" WHERE account_type_id IN
            (SELECT id FROM account_types
                WHERE name = '{types}')"""
    elif types:
        sql_statement += f""" WHERE account_type_id IN
        (SELECT id FROM account_types 
            WHERE name in {types})"""
    df: pd.DataFrame = pd.read_sql_query(sql_statement, DbSetup.engine)

    df["balance"] = 0.0
    df["start_date"] = datetime.strftime(balance_start_date, "%Y-%m-%d")
    df["end_date"] = datetime.strftime(balance_end_date, "%Y-%m-%d")
    df["last_updated"] = datetime.strftime(datetime.today(), "%Y-%m-%d")
    df["uncategorized_transactions"] = 0
    df["account_type"] = ""

    with DbSetup.Session() as session:
        ids: list[int] = df["id"].to_list()

        account_objs = session.query(Account).filter(Account.id.in_(ids)).all()

        for account in account_objs:
            df.loc[df["id"] == account.id, "balance"] = account.balance(
                balance_start_date, balance_end_date
            )
            df.loc[df["id"] == account.id, "uncategorized_transactions"] = len(
                account.uncategorized_transactions(
                    balance_start_date, balance_end_date
                )
            )
            df.loc[df["id"] == account.id, "last_updated"] = datetime.strftime(
                account.last_updated(), "%Y-%m-%d"
            )
            df.loc[
                df["id"] == account.id, "account_type"
            ] = account.account_type.name

    return dict_to_json(df.to_dict(), df.index)


def add_new_account_to_db(
    name: str, account_type_id: int, account_type_label: str, debit_inc: bool
) -> dict:
    """Add an account to the database with the given name, type/group
    it's a part of, and whether it increases with debits or not.

    Parameters
    -----------
        name (str) : The name of the account- what it will appear as
            accross the app and on the balance sheet/expense report.
        account_type_id (int) : The id for the account_type that the
            account should be. This will come from the user in a
            form request when creating a new account.
        account_type_label (str) : The label for the account group to
            add this account to.
        debit_inc (bool): Whether debits to the account increase the
            balance or not.

    Returns
    -------
        (dict) : A dictionary contianing a message, error information
        (if relevant), and account_id of the new account in the database.
    """
    account_id: int = 0

    with DbSetup.Session() as session:
        try:
            # Create a new account Type if the id is -1.
            if account_type_id == -1:
                new_acct_type: AccountType = AccountType(
                    name=account_type_label,
                    group="Misc.",
                )
                session.add(new_acct_type)
                session.commit()

                account_type_id = (
                    session.query(AccountType)
                    .filter(AccountType.name == account_type_label)
                    .first()
                    .id
                )

            new_acct: Account = Account(
                name=name,
                account_type_id=account_type_id,
                debit_inc=debit_inc,
            )

            session.add(new_acct)

            account_id = new_acct.id

            session.commit()

        except Exception as e:
            return dict(
                message="There was a problem posting the new account.",
                error=str(e),
            )

    return dict(
        message="SUCCESS",
        account_name=name,
        account_id=account_id,
    )


def account_balances(account_ids: list[int]) -> dict:
    """Calculate and return the account balances of the
    given list of account ids.

    Parameters
    ----------
        account_ids (list of ints) : The list of account ids to
            calculate the balance for.

    Returns
    -------
        id_to_balance (dict of ints to floats) : A map of account id to account
            balance.
    """
    id_to_balance: dict = dict()

    with DbSetup.Session() as session:

        for id in account_ids:
            account: Account = (
                session.query(Account).filter(Account.id == id).scalar()
            )
            id_to_balance[account.id] = account.balance()

    return id_to_balance
