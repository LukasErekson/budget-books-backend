from flask import Flask
from sqlalchemy import Inspector, inspect

from budget_book_backend import __version__
from budget_book_backend.models.db_setup import DbSetup


def test_version():
    assert __version__ == "0.1.0"


def test_app_creation(app: Flask):
    """Test whether the app gets created with the routes and database."""
    route_keys: list[str] = list(app.blueprints.keys())

    assert route_keys == [
        "accounts",
        "account_types",
        "transactions",
    ]

    assert app.config.get("DATABASE") == "sqlite:///tests/test.db"


def test_database_setup(use_test_db):
    """Test that the database gets set up and that DbSetup has the
    proper file and tables associated with it."""
    assert str(DbSetup.engine.url) == "sqlite:///tests/test.db"

    inspector: Inspector = inspect(DbSetup.engine)

    tables: list[str] = inspector.get_table_names()

    assert tables != []
