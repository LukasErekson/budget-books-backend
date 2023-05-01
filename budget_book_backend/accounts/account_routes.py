import json

from flask import Blueprint, request
from datetime import datetime

from budget_book_backend.accounts.account_services import (
    account_balances,
    get_accounts_by_type,
    add_new_account_to_db,
)
from budget_book_backend.utils.utils import (
    endpoint_error_wrapper,
    validate_and_get_json,
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

    types: tuple[str, ...] = ()

    if account_type == "bank":
        types = ("Checking Account", "Savings Account", "Credit Card")
    else:
        types = tuple(account_type.split(","))
        if len(types) == 1:
            types = (types[0],)

    balance_start_date: datetime | str = request.args.get(
        "balance_start_date", datetime(1, 1, 1)
    )
    balance_end_date: datetime | str = request.args.get(
        "balance_end_date", datetime.now()
    )

    if isinstance(balance_start_date, str):
        balance_start_date = datetime.strptime(balance_start_date, "%Y-%m-%d")

    if isinstance(balance_end_date, str):
        balance_end_date = datetime.strptime(balance_end_date, "%Y-%m-%d")

    accounts: list[dict] = get_accounts_by_type(
        types, balance_start_date, balance_end_date
    )

    return (
        json.dumps(
            dict(
                message="SUCCESS",
                accounts=accounts,
            )
        ),
        200,
    )


@endpoint_error_wrapper
@accounts_routes.route(f"{BASE_ACCOUNTS_URL}", methods=["POST"])
def add_new_account():
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
    request_json = validate_and_get_json()

    name: str = request_json["name"]
    account_type_id: int = int(request_json["account_type"]["value"])
    account_type_label: str = request_json["account_type"]["label"]
    debit_inc: bool = request_json["debit_inc"]

    response: dict = add_new_account_to_db(
        name, account_type_id, account_type_label, debit_inc
    )

    return (
        json.dumps(response),
        200 if "serverError" not in response else 500,
    )


@endpoint_error_wrapper
@accounts_routes.route(f"{BASE_ACCOUNTS_URL}/balances", methods=["GET"])
def get_account_balances():
    account_ids: list | int | str = request.args.get("account_ids", [])

    if isinstance(account_ids, int):
        account_ids = [account_ids]
    if isinstance(account_ids, str):
        account_ids = [int(account_ids)]
    elif isinstance(account_ids, str):
        account_ids = map(int, account_ids.split(","))

    response_dict: dict = account_balances(account_ids)

    return json.dumps(dict(message="SUCCESS", balances=response_dict)), 200
