from models.db_setup import DbSetup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.account import Account
from models.account_type import AccountType
from models.transaction import Transaction


def main(file_name: str, test: bool = True):
    """Create a Database and add the models (tables) to it."""
    DbSetup.engine = create_engine("sqlite:///" + file_name)
    DbSetup.Session = sessionmaker(bind=DbSetup.engine)
    DbSetup.add_tables()

    if test:
        credit_card = AccountType(name="Credit Card", group="Liabilities")
        amex = Account(
            name="AMEX",
            debit_inc=False,
            account_type_id=1,
        )
        trans1 = Transaction(
            name="Test Transaction",
            description="This is a test transaction",
            amount=25.43,
            credit_account_id=1,
        )
        payment1 = Transaction(
            name="Auto Payment",
            description="Auto pay",
            amount=25.43,
            debit_account_id=1,
        )
        with DbSetup.Session() as session:
            session.add_all([credit_card, amex, trans1, payment1])
            session.commit()

    else:
        # Basic Assets
        with DbSetup.Session() as session:
            for asset_name in [
                "Checking Account",
                "Savings Account",
                "Roth IRA",
            ]:
                session.add(AccountType(name=asset_name, group="Assets"))
                session.commit()

        # Liabilities
        # with DbSetup.Session() as session:
        #     for asset_name in ["Credit Card"]:
        #         session.add(AccountType(name=asset_name, group="Liabilities"))
        #         session.commit()

        # Expenses
        with DbSetup.Session() as session:
            for asset_name in [
                "Groceries",
                "Rent",
                "Gas",
                "Education",
                "Entertainment",
                "Doctor",
                "Prescriptions",
                "Therapy",
                "Pet Expenses",
                "Clothing",
                "Gifts (Given)",
                "Taxes",
                "Travel",
            ]:
                session.add(AccountType(name=asset_name, group="Expenses"))
                session.commit()

        # Income
        with DbSetup.Session() as session:
            for asset_name in [
                "Paycheck",
                "Credit Card Rewards",
                "Interest Income",
                "Reimbursement",
                "Gifts (Received)",
            ]:
                session.add(AccountType(name=asset_name, group="Income"))
                session.commit()

        # Equity
        with DbSetup.Session() as session:
            for asset_name in ["Opening Balance Equity"]:
                session.add(AccountType(name=asset_name, group="Equity"))
                session.commit()


if __name__ == "__main__":
    main("budget_book_backend/models/databases/database.db", False)
