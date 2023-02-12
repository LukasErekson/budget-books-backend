import json
import pandas as pd

from flask import Blueprint, request
from datetime import datetime
from typing import Mapping

from .account_services import account_balances
from models.db_setup import DbSetup
from models.account import Account
from models.account_type import AccountType
from resources.utils import (
    dict_to_json,
    endpoint_error_wrapper,
)


accounts_routes: Blueprint = Blueprint("accounts", __name__)

BASE_ACCOUNTS_URL: str = "/api/accounts"


@endpoint_error_wrapper
@accounts_routes.route(f"{BASE_ACCOUNTS_URL}", methods=["GET"])
def get_accounts():
    """Return all the accounts that are associated with the user,
    listing their id, name, balance (as of today), and whether they
    are a debit increase account or not.

    Request Arguments
    -----------------
        account_type (str) : The type of accounts to fetch. Usually, one of
            "bank", "category", or "all". Defaults to "all"
        balance_start_date (date str) : When computing account
            balances, use this as the start date. Optional.
        balance_end_date (date str) : When computing account
            balances, use this as the end date. Optional.

    Example url:
        ?balance_start_date=2022-10-02&account_type=bank
    """
    account_type: str = request.args.get("account_type", "all")

    types: tuple[str] | str = ()

    if account_type == "bank":
        types = ("Checking Account", "Savings Account", "Credit Card")
    else:
        types = tuple(account_type.split(","))
        if len(types) == 1:
            types = types[0]

    balance_start_date: str = request.args.get(
        "balance_start_date", datetime(1, 1, 1)
    )
    balance_end_date: str = request.args.get(
        "balance_end_date", datetime.now()
    )

    if isinstance(balance_start_date, str):
        balance_start_date = datetime.strptime(balance_start_date, "%Y-%m-%d")

    if isinstance(balance_end_date, str):
        balance_start_date = datetime.strptime(balance_end_date, "%Y-%m-%d")

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

    return (
        dict(
            message="SUCCESS",
            accounts=json.dumps(dict_to_json(df.to_dict(), df.index)),
        ),
        200,
    )


@endpoint_error_wrapper
@accounts_routes.route(f"{BASE_ACCOUNTS_URL}", methods=["POST"])
def add_new_account(self):
    """Add a new account.

    JSON Parameters
    ---------------
        name (str) : The name of the account- what it will appear as
            accross the app and on the balance sheet/expense report.
        account_type_id (int) : The id for the account_type that the
            account should be. This will come from the user in a
            form request when creating a new account.
        debit_inc (bool): Whether debits to the account increase the
            balance or not.

    Example request.json:
    {
        "name": "American Express CC",
        "account_type_id": "1",
        "debit_inc": false
    }
    """
    request_json: Mapping = request.get_json()

    account_id: int = 0

    with DbSetup.Session() as session:
        try:
            # Create a new account Type if the id is -1.
            account_type_id: int = int(request_json["account_type"]["value"])
            if account_type_id == -1:
                new_acct_type: AccountType = AccountType(
                    name=request_json["account_type"]["label"],
                    group="Misc.",
                )
                session.add(new_acct_type)
                session.commit()

                account_type_id = (
                    session.query(AccountType)
                    .filter(
                        AccountType.name
                        == request_json["account_type"]["label"]
                    )
                    .first()
                    .id
                )

            new_acct: Account = Account(
                name=request_json["name"],
                account_type_id=account_type_id,
                debit_inc=request_json["debit_inc"],
            )

            session.add(new_acct)

            account_id = new_acct.id

            session.commit()

        except Exception as e:
            return (
                json.dumps(
                    dict(
                        message="There was a problem posting the new account.",
                        error=str(e),
                    )
                ),
                500,
            )

    return (
        json.dumps(
            dict(
                message="SUCCESS",
                account_name=request_json["name"],
                account_id=account_id,
            )
        ),
        200,
    )


@endpoint_error_wrapper
@accounts_routes.route(f"{BASE_ACCOUNTS_URL}/balances", methods=["GET"])
def get_account_balances():
    account_ids: list | int = request.args.get("account_ids", [])

    if isinstance(account_ids, int):
        account_ids = [account_ids]
    elif isinstance(account_ids, str):
        account_ids = map(int, account_ids.split(","))

    response_dict: dict = account_balances(account_ids)

    return json.dumps(response_dict), 200
