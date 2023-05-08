from typing import Any, Generator

import pytest
from flask import Flask
from flask.testing import FlaskClient
from sqlalchemy import Inspector, inspect, text

from budget_book_backend import create_app
from budget_book_backend.models.db_setup import DbSetup
from tests.setup_db import setup_db


@pytest.fixture
def app() -> Flask:
    """Initlaize the flask app for testing purposes."""
    test_app: Flask = create_app(
        test_config=dict(DATABASE="sqlite:///tests/test.db")
    )

    return test_app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Expose the client of the app being used to mock requests."""
    return app.test_client()


@pytest.fixture(scope="function")
def use_test_db(app: Flask) -> Generator[None, Any, None]:
    """Set up, expose, and take down the database used for the tests."""

    setup_db(test=False)

    with app.app_context():
        DbSetup.set_engine()

    yield

    # Tear down the test databse
    inspector: Inspector = inspect(DbSetup.engine)
    with DbSetup.engine.connect() as conn:
        for table in inspector.get_table_names():
            conn.execute(text(f"DROP TABLE IF EXISTS {table};"))
