from models.account import Account
from models.db_setup import DbSetup


def account_balances(account_ids: list[int]) -> dict:
    """Calculate and return the account balances of the
    given list of account ids.

    Parameters
    ----------
        account_ids (list of ints) : The list of account ids to
            calculate the balance for.

    Returns
    -------
        id_to_balance (dict of ints to floats) : A map of account id to account
            balance.
    """
    id_to_balance: dict = dict()

    with DbSetup.Session() as session:

        for id in account_ids:
            account: Account = (
                session.query(Account).filter(Account.id == id).scalar()
            )
            id_to_balance[account.id] = account.balance()

    return id_to_balance
