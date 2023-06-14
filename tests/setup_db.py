from budget_book_backend.models.account import Account
from budget_book_backend.models.account_type import AccountType
from budget_book_backend.models.db_setup import DbSetup
from budget_book_backend.models.transaction import Transaction
from tests.test_data.account_type_test_data import ACCOUNT_TYPES


def setup_db(test: bool = True) -> None:
    """Create a Database and add the models (tables) to it."""
    # DbSetup.engine = create_engine("sqlite:///" + file_name)
    # DbSetup.Session = sessionmaker(bind=DbSetup.engine)
    DbSetup.add_tables()

    with DbSetup.Session() as session:
        for account_type_dict in ACCOUNT_TYPES:
            session.add(
                AccountType(
                    name=account_type_dict["name"],
                    group=account_type_dict["group"],
                )
            )
        session.commit()

    if test:
        from tests.test_data.account_test_data import ACCOUNTS
        from tests.test_data.transaction_test_data import TRANSACTIONS

        with DbSetup.Session() as session:
            for account in ACCOUNTS:
                session.add(
                    Account(
                        name=account["name"],
                        debit_inc=account["debit_inc"],
                        account_type_id=account["account_type_id"],
                    )
                )

            session.commit()

            for transaction in TRANSACTIONS:
                session.add(
                    Transaction(
                        name=transaction["name"],
                        description=transaction["description"],
                        amount=transaction["amount"],
                        credit_account_id=transaction.get("credit_account_id"),
                        debit_account_id=transaction.get("debit_account_id"),
                        transaction_date=transaction["transaction_date"],
                    )
                )

            session.commit()


if __name__ == "__main__":
    setup_db(False)
    # "budget_book_backend/models/databases/database.db"
