from flask import Blueprint, request

import json
from budget_book_backend.utils import endpoint_error_wrapper

from .transaction_services import (
    get_transactions_by_account,
    add_new_transactions,
    categorize_transactions,
    update_transactions,
    remove_transactions,
)


transaction_routes: Blueprint = Blueprint("transactions", __name__)

BASE_TRANSACTION_URL: str = "/api/transactions"


@endpoint_error_wrapper
@transaction_routes.route(f"{BASE_TRANSACTION_URL}", methods=["GET"])
def get_transactions():
    """Return all the transactions that are associated with the
    account_id OR all of the given transaction categories.

    Example of arguments:
        ?account_ids=1,2
    """
    url_account_ids: str | None = request.args.get("account_ids")

    if url_account_ids is None:
        return (
            json.dumps(
                dict(
                    message="ERROR", error="URL is missing account_ids values."
                )
            ),
            400,
        )

    account_id_strings: list[str] = list(
        filter(lambda id: id, url_account_ids.split(","))
    )

    if len(account_id_strings) == 0:
        return (
            json.dumps(
                dict(message="ERROR: No account_ids found in the request."),
            ),
            500,
        )

    account_ids: list[int] = list(map(int, account_id_strings))
    categorize_type: str = request.args.get("categorize_type", "all")

    transactions: list[dict] = get_transactions_by_account(
        account_ids, categorize_type
    )

    return_dict: dict = {
        "message": "SUCCESS",
        "transactions": transactions,
    }

    return (json.dumps(return_dict), 200)


@endpoint_error_wrapper
@transaction_routes.route(f"{BASE_TRANSACTION_URL}", methods=["POST"])
def post_new_transactions():
    """Add new transaction(s) to the respective accounts.

    Example request.json:
    {
        "transactions": [
            {
                "name": "Test Post",
                "description": "A Postman test to write to the database.",
                "amount": "50.24",
                "credit_account_id": "1",
                "transaction_date": "2022-10-02"
            }
        ]
    }
    """
    request_json: dict = request.get_json()

    transactions: list[dict] = request_json.get("transactions", [])

    status_dict: dict = add_new_transactions(transactions)

    return (
        json.dumps(status_dict),
        200,
    )


@endpoint_error_wrapper
@transaction_routes.route(f"{BASE_TRANSACTION_URL}", methods=["PUT"])
def put_category():
    """Categorize the given transaction(s) to their respective
        category accounts.

        Example request.json:
    {
        "transactions": [
        {
            "transaction_id": "1",
            "category_id": "1",
            "debit_or_credit": "debit"
        }
        ]
    }
    """
    request_json: dict = request.get_json()

    transactions: list[dict] = request_json.get("transactions", [])

    status_dict: dict = categorize_transactions(transactions)

    return (
        json.dumps(status_dict),
        200,
    )


@endpoint_error_wrapper
@transaction_routes.route(f"{BASE_TRANSACTION_URL}", methods=["PATCH"])
def patch():
    """Change existing transaction(s) to have new values.

    Example request.json:
    {
        "transactions": [
            {
            "id": "2",
            "name": "Test Post",
            "description": "A Postman test to write to the database.",
            "amount": "50.24",
            "credit_account_id": "1",
            "transaction_date": "2022-10-02"
            }
        ]
    }
    """
    request_json: dict = request.get_json()

    transactions: list[dict] = request_json.get("transactions", [])

    status_dict: dict = update_transactions(transactions)

    return (
        json.dumps(status_dict),
        200,
    )


@endpoint_error_wrapper
@transaction_routes.route(f"{BASE_TRANSACTION_URL}/<id>", methods=["PUT"])
def edit(id: int) -> tuple[str, int]:
    """Change existing transaction(s) to have new values.

    Example request.json:
    {
        "transactions": [
            {
            "id": "2",
            "name": "Test Post",
            "description": "A Postman test to write to the database.",
            "amount": "50.24",
            "credit_account_id": "1",
            "transaction_date": "2022-10-02"
            }
        ]
    }
    """
    request_json: dict = request.get_json()

    edited_transaction: dict = request_json.get("transaction", {})

    edited_transaction["transaction_id"] = id

    status_dict: dict = update_transactions([edited_transaction])

    return json.dumps(status_dict), 200


@endpoint_error_wrapper
@transaction_routes.route(f"{BASE_TRANSACTION_URL}", methods=["DELETE"])
def delete():
    """Delete transaction(s) with given ID(s).

    Example request.json:
    {
        "user_id": "0",
        "transaction_ids": [1, 2]
    }
    """
    request_json: dict = request.get_json()

    transaction_ids: list[int] = request_json.get("transaction_ids", [])

    status_dict: dict = remove_transactions(transaction_ids)

    return (
        json.dumps(status_dict),
        200,
    )
