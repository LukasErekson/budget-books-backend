from typing import TYPE_CHECKING

# Avoid circular imports but still use type checking.
if TYPE_CHECKING:
    from .account import Account

from sqlalchemy import Float, ForeignKey, String, DateTime
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import datetime

from .db_setup import DbSetup


class Transaction(DbSetup.Base):
    """ORM for individual transactions.

    Each transaction always have a unique ID, a name, a description, an
    amount, and an account of origin. Depnding on whether it is a debit
    or credit for its origin account, credit/debit may be null (the
    complement of what it is for its origin account, to be determined
    when the transaction is created and added to the table.)
    """

    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    description: Mapped[str] = mapped_column(String)
    amount: Mapped[float] = mapped_column(Float(precision=2))
    debit_account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id"), nullable=True
    )
    credit_account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id"), nullable=True
    )
    debit_account: Mapped["Account"] = relationship(
        "Account",
        foreign_keys=[debit_account_id],
        backref="debit_transactions",
    )
    credit_account: Mapped["Account"] = relationship(
        "Account",
        foreign_keys=[credit_account_id],
        backref="credit_transactions",
    )
    transaction_date: Mapped[DateTime] = mapped_column(
        DateTime, default=datetime.now()
    )
    date_entered: Mapped[DateTime] = mapped_column(
        DateTime, default=datetime.now()
    )

    def __repr__(self):
        return (
            f"<Transaction id={self.id} name={self.name}, "
            f"amount={self.amount}>"
        )
