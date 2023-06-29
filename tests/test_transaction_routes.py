import json

import pytest
from flask.testing import FlaskClient
from werkzeug.test import TestResponse

from budget_book_backend.models.transaction import Transaction
from budget_book_backend.transactions.transaction_routes import (
    BASE_TRANSACTION_URL,
    delete,
    get_transactions,
    patch,
    post_new_transactions,
    put_category,
)


def test_base_url_get_failure(client: FlaskClient, use_test_db) -> None:
    """Expect a request without the account_ids specified as URL
    parameters to return a 400 status and contain more error information
    within the response dict.
    """
    with client as cli:
        response: TestResponse = cli.get(
            f"{BASE_TRANSACTION_URL}",
            content_type="application/json",
        )

    assert response.status_code == 400

    response_data: dict = json.loads(response.data)

    assert response_data.get("message") == "ERROR"

    assert response_data.get("error")
