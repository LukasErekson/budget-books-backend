from sqlalchemy import Column, Float, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from models.db_setup import DbSetup


class Transaction(DbSetup.Base):
    """ORM for individual transactions.

    Each transaction always have a unique ID, a name, a description, an
    amount, and an account of origin. Depnding on whether it is a debit
    or credit for its origin account, credit/debit may be null (the
    complement of what it is for its origin account, to be determined
    when the transaction is created and added to the table.)
    """

    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    name = Column(String(120))
    description = Column(String)
    amount = Column(Float(precision=2))
    debit_account_id = Column(ForeignKey("accounts.id"), nullable=True)
    credit_account_id = Column(ForeignKey("accounts.id"), nullable=True)
    debit_account = relationship(
        "Account",
        foreign_keys=[debit_account_id],
        backref="debit_transactions",
    )
    credit_account = relationship(
        "Account",
        foreign_keys=[credit_account_id],
        backref="credit_transactions",
    )
    transaction_date = Column(DateTime, default=datetime.now())
    date_entered = Column(DateTime, default=datetime.now())

    def __repr__(self):
        return (
            f"<Transaction id={self.id} name={self.name}, "
            f"amount={self.amount}>"
        )
