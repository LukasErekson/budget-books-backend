from datetime import datetime
from typing import Optional

import pandas as pd
from sqlalchemy import select, text

from budget_book_backend.models.account import Account
from budget_book_backend.models.account_type import AccountType
from budget_book_backend.models.db_setup import DbSetup
from budget_book_backend.utils import dict_to_json


def get_accounts_by_type(
    types: tuple[str, ...],
    balance_start_date: datetime,
    balance_end_date: datetime,
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
    with DbSetup.Session() as session:
        if types[0] != "all":
            account_types: tuple[AccountType, ...] = tuple(
                session.scalars(
                    select(AccountType).where(AccountType.name.in_(types))
                ).all()
            )
        else:
            account_types = tuple(session.scalars(select(AccountType)).all())

        ids: tuple | str = tuple(
            map(lambda account_type: account_type.id, account_types)
        )

        account_objs: list[Account] = list(
            session.scalars(select(Account).where(Account.account_type_id.in_(ids)))
        )

        # Special case where a singular value in a tuple
        # isn't formatted right for SQL queries.
        if len(ids) == 1:
            ids = f"({ids[0]})"

        accounts_df: pd.DataFrame = pd.read_sql_query(
            text(f"SELECT * FROM accounts WHERE account_type_id IN {ids}"),
            DbSetup.engine.connect(),
            index_col="id",
        )

        accounts_df["balance"] = 0.0
        accounts_df["start_date"] = datetime.strftime(balance_start_date, "%Y-%m-%d")
        accounts_df["end_date"] = datetime.strftime(balance_end_date, "%Y-%m-%d")
        accounts_df["last_updated"] = datetime.strftime(datetime.today(), "%Y-%m-%d")
        accounts_df["uncategorized_transactions"] = 0
        accounts_df["account_type"] = ""
        accounts_df["account_group"] = ""
        accounts_df["id"] = accounts_df.index

        for account in account_objs:
            accounts_df.loc[account.id, "balance"] = account.balance(
                balance_start_date, balance_end_date
            )
            accounts_df.loc[account.id, "uncategorized_transactions"] = len(
                account.uncategorized_transactions(balance_start_date, balance_end_date)
            )
            accounts_df.loc[account.id, "last_updated"] = datetime.strftime(
                account.last_updated(), "%Y-%m-%d"
            )
            accounts_df.loc[account.id, "account_type"] = account.account_type.name
            accounts_df.loc[
                account.id, "account_group"
            ] = account.account_type.group_name

    return dict_to_json(accounts_df.to_dict(), accounts_df.index)


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
                new_account_type: Optional[AccountType] = (
                    session.query(AccountType)
                    .filter(AccountType.name == account_type_label)
                    .first()
                )

                if new_account_type is None:
                    new_acct_type: AccountType = AccountType(
                        name=account_type_label,
                        group_name="Misc.",
                    )
                    session.add(new_acct_type)
                    session.commit()

                # Attempt to query again
                new_account_type = (
                    session.query(AccountType)
                    .filter(AccountType.name == account_type_label)
                    .first()
                )

                if new_account_type is None:
                    raise Exception(
                        "The new AccountType ID could not be found. \
                        There may have been a problem saving it to the \
                        database."
                    )

                account_type_id = new_account_type.id

            new_acct: Account = Account(
                name=name,
                account_type_id=account_type_id,
                debit_inc=debit_inc,
            )

            session.add(new_acct)

            session.commit()

            account_id = new_acct.id

        except Exception as e:
            return dict(
                message="There was a problem posting the new account.",
                serverError=str(e),
            )

    return dict(
        message="SUCCESS",
        account_name=name,
        account_id=account_id,
    )


def account_balances(account_ids: list[int]) -> dict[int, float]:
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
            account: Account | None = session.get(Account, id)

            if account is None:
                continue

            id_to_balance[account.id] = account.balance()

    return id_to_balance


def update_account_info(edit_account: dict) -> dict:
    """Update a given account's info in the databse.

    Paramters
    ---------
        edit_account (dict) : A dictionary with all the
            required Account information, including ID,
            name, account type, etc.

    Returns
    -------
        (dict) : Response dictionary indicating whether or not
            the updatd was successful in the database.
    """
    new_name: str = edit_account["name"]
    new_account_type_id: int = edit_account["account_type_id"]
    new_debit_inc: bool = edit_account["debit_inc"]

    if not new_name:
        return dict(message="ERROR", error="Account name cannot be blank.")

    with DbSetup.Session() as session:
        account: Account | None = session.get(Account, edit_account["id"])

        if account is None:
            raise Exception(f'Account with ID {edit_account["id"]} cannot be found.')

        account.name = new_name
        account.account_type_id = new_account_type_id
        account.debit_inc = new_debit_inc

        session.commit()

    return dict(message="SUCCESS")


def delete_account(delete_account_id: int) -> dict:
    """Remove a given account from the database.

    Parameters
    ----------
        delete_account_id (int) : The ID of the account to delete.

    Returns
    -------
        (dict) : Response dictionary indicating whether or not is was successful.
    """
    with DbSetup.Session() as session:
        account: Account | None = session.get(Account, delete_account_id)

        if account is None:
            raise Exception(f"Account with ID {delete_account_id} cannot be found.")

        session.delete(account)

        session.commit()

    return dict(message="SUCCESS")


def account_net_changes_by_group(
    account_groups: list[str],
    date_ranges: list[str] = [datetime.today().strftime("%Y-%m-%d")],
) -> dict:
    """Return the account balances by the selected account groups within
    the given date ranges.

    Parameters
    ----------
        account_groups (list[str]) : The names of the account groups to
            grab the balances of.
        date_ranges (list[str]) : The dates between which to return the
            balances of the different accounts within the account groups.
            This list is assumed to be of even length of at least 2.

    Returns
    -------
        account_balances (dict) : A dictionary containing the account
            balances of the following form:
                {
                    "dates": date_ranges,
                    "account_group_1": {
                        "account_type 1": {
                            "account 1": [balance1, balance2, ...]
                        }
                    }
                }
    """
    # If only given one date, assume the first date is the earliest possible.
    if len(date_ranges) == 1:
        date_ranges.insert(0, "0001-01-1")

    account_balances: dict = {
        "dates": date_ranges,
        "message": "SUCCESS",
    }

    for group in account_groups:
        account_balances[group] = {}

    with DbSetup.Session() as session:
        account_types: Optional[list[AccountType]] = (
            session.query(AccountType)
            .filter(AccountType.group_name.in_(account_groups))
            .all()
        )

        if account_types is None:
            return dict(
                message="ERROR",
                error=f"There was a problem getting the account types associated with {', '.join(account_groups)}",
            )

        account_type_ids: list[int] = [acct_type.id for acct_type in account_types]

        accounts: Optional[list[Account]] = (
            session.query(Account)
            .filter(Account.account_type_id.in_(account_type_ids))
            .all()
        )

        if accounts is None:
            return dict(
                message="ERROR",
                error=f"There was a problem getting the accounts associated with {', '.join(account_types)}",
            )

        for account in accounts:
            account_group: str = account.account_type.group_name
            account_type: str = account.account_type.name

            account_balances[account_group].setdefault(account_type, dict())

            account_balances[account_group][account_type][account.name] = [
                account.balance(
                    datetime.strptime(date_ranges[i], "%Y-%m-%d"),
                    datetime.strptime(date_ranges[i + 1], "%Y-%m-%d"),
                )
                * ((-1) ** (account.debit_inc))
                for i in range(0, len(date_ranges), 2)
            ]

    return account_balances
