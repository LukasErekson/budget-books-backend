import pandas as pd
from sqlalchemy import text

from budget_book_backend.models.account_type import AccountType
from budget_book_backend.models.db_setup import DbSetup
from budget_book_backend.utils import dict_to_json


def get_account_types(group: str = "all") -> list[dict]:
    """Return all the account types, with their names and groups,
    with the requested group type. If no group type is given, it
    returns all of them.

    Parameters
    ----------
        group (str) : (Optional) The group of account_types or
            categories to get. This can be "income", "assets",
            "liabilities", "expenses", etc.

    Returns
    -------
        (dict) : A dictionary of account types mapping from their id to
            their information.
    """
    sql_statement: str = """SELECT * FROM account_types """

    if group != "all":
        sql_statement += f" WHERE \"group_name\" = '{group}'"

    df: pd.DataFrame = pd.read_sql_query(
        text(sql_statement), DbSetup.engine.connect()
    )

    return dict_to_json(df.to_dict(), df.index)


def create_account_type(name: str, group: str = "Misc.") -> dict:
    """Add a new account type to the database.

    Parameters
    ----------
        name (str) : The name of the account type- what it will
            appear as accross the app and on the balance
            sheet/expense report.
        group (str) : The name of the group that it's a part of.

    Returns
    -------
        (dict) : A dictionary with a message indicating whether or not
            an exception was thrown and the account type name.
    """
    if not name:
        return dict(
            message="There was a problem posting the new account type.",
            error="Cannot create an account type without a name.",
            account_name=name,
        )

    with DbSetup.Session() as session:
        try:
            new_acct_type: AccountType = AccountType(
                name=name, group_name=group
            )

            session.add(new_acct_type)

            session.commit()

        except Exception as e:
            return dict(
                message="There was a problem posting the new account type.",
                error=str(e),
                account_name=name,
            )

    return dict(message="SUCCESS", account_name=name)


def get_account_type_groups() -> dict[str, str | list]:
    """Fetch all the Account Type groups.

    Returns
    -------
        (dict) : A dictionary with a message indicating whether or not
            an exception was thrown and the account type name.
    """
    account_groups: list = []

    with DbSetup.Session() as session:
        try:
            account_groups = []

        except Exception as e:
            return dict(message="ERROR", error=str(e))

    return dict(message="SUCCESS", account_groups=[])
