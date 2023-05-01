from os import path
from typing import Mapping, Optional
from flask import Flask

from budget_book_backend.accounts.account_routes import accounts_routes
from budget_book_backend.account_types.account_type_routes import (
    account_type_routes,
)
from budget_book_backend.transactions.transaction_routes import (
    transaction_routes,
)

from budget_book_backend.models.db_setup import DbSetup


def create_app(test_config: Optional[Mapping] = None) -> Flask:
    """Flask app function factory definition"""
    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE="sqlite:///"
        + path.join(path.dirname(__file__), "models/databases/database.db"),
    )

    print(app.config.get("DATABASE"))

    if test_config:
        app.config.from_mapping(test_config)

    with app.app_context():
        DbSetup.set_engine()
        DbSetup.add_tables()

    app.register_blueprint(accounts_routes)
    app.register_blueprint(account_type_routes)
    app.register_blueprint(transaction_routes)

    return app


def main(debug: bool = False) -> None:
    """Create and run the Flask app."""
    app = create_app()
    app.run(debug=debug)


if __name__ == "__main__":
    main(True)
