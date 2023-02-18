import json

from flask import Blueprint, request
from typing import Mapping

from account_types.account_type_services import (
    get_account_types,
    create_account_type,
)
from utils import (
    endpoint_error_wrapper,
)

account_type_routes: Blueprint = Blueprint("account_types", __name__)

BASE_ACCOUNT_TYPE_URL: str = "/api/accounttypes/"


@endpoint_error_wrapper
@account_type_routes.route(f"{BASE_ACCOUNT_TYPE_URL}", methods=["GET"])
def account_types():
    """Return all the account types, with their names and groups,
    with the requested group type. If no group type is given, it
    returns all of them.

    Request Arguments
    -----------------
        group (str) : (Optional) The group of account_types or
            categories to get. This can be "income", "assets",
            "liabilities", "expenses", etc.

    Example url:
        ?group=liabilities
    """
    group: str = request.args.get("group", "all")

    account_types: dict = get_account_types(group)

    return (
        dict(
            message="SUCCESS",
            account_types=account_types,
        ),
        200,
    )


@endpoint_error_wrapper
@account_type_routes.route(f"{BASE_ACCOUNT_TYPE_URL}", methods=["POST"])
def add_new_account_type():
    """Add a new account type.

    JSON Parameters
    ---------------
        name (str) : The name of the account type- what it will
            appear as accross the app and on the balance
            sheet/expense report.
        group (str) : The name of the group that it's a part of.

    Example request.json:
    {
        "name": "Credit Union Checking",
        "group": "Assets"
    }
    """
    request_json: Mapping = request.get_json()
    name: str = request_json.get("name")
    group: str = request_json.get("group", "Misc.")

    if name is None:
        return (
            json.dumps(dict(message="Please include a name in the request.")),
            500,
        )

    response_dict: dict = create_account_type(name, group)

    return json.dumps(response_dict), 200
