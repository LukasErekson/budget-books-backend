import pytest

from flask import Flask
from budget_book_backend import create_app
from budget_book_backend.models.db_setup import DbSetup
from sqlalchemy import inspect, Inspector, text

from tests.setup_db import setup_db


@pytest.fixture
def app():
    """Initlaize the flask app for testing purposes."""
    test_app: Flask = create_app(
        test_config=dict(DATABASE="sqlite:///tests/test.db")
    )

    yield test_app


@pytest.fixture
def client(app: Flask):
    """The client fixture for the flask app fixture."""
    return app.test_client()


@pytest.fixture(scope="function")
def use_test_db(app: Flask):
    """Set up the database used for running tests."""

    setup_db(test=True)

    with app.app_context():
        DbSetup.set_engine()

    yield

    # Tear down the test databse
    inspector: Inspector = inspect(DbSetup.engine)
    with DbSetup.engine.connect() as conn:
        for table in inspector.get_table_names():
            conn.execute(text(f"DROP TABLE IF EXISTS {table};"))
