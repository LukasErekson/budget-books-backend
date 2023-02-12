from sqlalchemy import Column, Boolean, Integer, String, ForeignKey
from datetime import datetime
from sqlalchemy.orm import relationship
from models.account_type import AccountType
from models.transaction import Transaction

from models.db_setup import DbSetup


class Account(DbSetup.Base):
    """ORM for individual accounts.

    Each account always has an ID, a name, a balance, and whether or not
    debits increase or decrease the account.
    """

    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)
    name = Column(String(120))
    account_type_id = Column(ForeignKey("account_types.id"), nullable=False)
    account_type = relationship(
        "AccountType",
        foreign_keys=[account_type_id],
        backref="accts",
    )
    debit_inc = Column(Boolean)

    # Also has properties debit_transactions and credit_transactions for
    # the transactions that change the account balance.

    def balance(
        self,
        start_date: datetime = datetime(1, 1, 1),
        end_date: datetime = datetime.now(),
    ) -> float:
        """Return the net change balance of the account between the two
        given dates by calculating:
        (-1*debit_inc)*(sum(credit_transactions) - sum(debit_transactions)).

        Parameters
        -----------
            start_date (datetime) : Optional. The starting date when the
                account balance will be considered 0. This is so that
                the net change can be calculated with this one function.
                If not given, defaults to the earliest datetime Python
                allows.
            end_date (datetime) : Optional. The date to calculate the
                account balance change up to. If not given, it defaults
                to now.

        Returns
        -------
            account_balance (float) : The net change of the account
                balance within the given timeframe.
        """

        def transaction_filter(transaction: Transaction) -> float:
            """Returns the amount of the transaction if within the given
            dates, otherwise returns 0.

            Parameters
            ----------
                transaction (Transaction) : The transaction to check
                    whether it's within the given dates.

            Returns
            -------
                (float) : The amount of the transaction. If not within
                    the given dates, returns 0.
            """

            if (
                transaction.credit_account_id is None
                or transaction.debit_account_id is None
            ):
                return 0.0

            t_date = transaction.transaction_date
            if t_date >= start_date and t_date <= end_date:
                return transaction.amount

            return 0.0

        final_balance: float = round(
            sum(map(transaction_filter, self.credit_transactions))
            - sum(map(transaction_filter, self.debit_transactions)),
            2,
        )

        if self.debit_inc:
            return -final_balance

        return final_balance

    def uncategorized_transactions(
        self,
        start_date: datetime = datetime(1, 1, 1),
        end_date: datetime = datetime.now(),
    ) -> list[Transaction]:
        """Return a list of the uncategorized transactions within the
        given timeframe.

        Parameters
        ----------
            start_date (datetime) : Optional. The starting date when the
                transactions will start to be considered.
                If not given, defaults to the earliest datetime Python
                allows.
            end_date (datetime) : Optional. The date to find the
                transactions up to. If not given, it defaults to now.

        Returns
        -------
            uncategorized_transactions (list of Transactions): The list
                of transaction objects that are uncategorized.
        """

        def transaction_filter(transaction: Transaction) -> bool:
            """Returns True if the transaction is within the given
            dates and is uncategorized, otherwise returns False.

            Parameters
            ----------
                transaction (Transaction) : The transaction to check
                    whether it's within the given dates.

            Returns
            -------
                (bool) : Whether the transaction is within the given
                    dates or not.
            """
            t_date = transaction.transaction_date
            if t_date >= start_date and t_date <= end_date:
                # Since it's associated with this account, only one or
                # the other will be None if uncategorized.
                return (
                    transaction.credit_account_id is None
                    or transaction.debit_account_id is None
                )

            return False

        uncategorized_transactions: list[Transaction] = list(
            filter(transaction_filter, self.credit_transactions)
        ) + list(filter(transaction_filter, self.debit_transactions))

        return uncategorized_transactions

    def last_updated(self) -> datetime:
        """Returns the date that the account was last updated (based on
        when the most recent transaciton in the database associated wtih
        the account).

        Returns
        -------
            (datetime) : The date of the most recent transaction that
                changes the account's balance. If no transactions are
                associated with the account, returns today's date.
        """
        if (
            len(self.credit_transactions) == 0
            and len(self.debit_transactions) == 0
        ):
            return datetime.now()

        credit_transactions_latest: datetime = datetime(1, 1, 1)
        debit_transactions_latest: datetime = datetime(1, 1, 1)

        if self.credit_transactions:
            credit_transactions_latest = max(
                [t.transaction_date for t in self.credit_transactions]
            )

        if self.debit_transactions:
            debit_transactions_latest = max(
                [t.transaction_date for t in self.debit_transactions]
            )

        return max(credit_transactions_latest, debit_transactions_latest)

    def __repr__(self):
        return (
            f"<Account id={self.id} name={self.name}, "
            f"type={self.account_type},  "
            f"debit_inc={self.debit_inc}>"
        )
