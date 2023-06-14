from tests.test_data.account_type_test_data import ACCOUNT_TYPES


def account_type_name_to_id(name: str) -> int:
    """Return the account_type ID for a given account_type name for the
    sake of mapping Accounts to Account Types in the test database.

    Parameters
    ----------
        name (str) : The name of the account_type to find the id of.

    Returns
    -------
        (int) : The ID of the account_type with the given name, or -1 if
            none is found.
    """
    for account_type in ACCOUNT_TYPES:
        if account_type["name"] == name:
            return account_type["id"]

    return -1


amex: dict = dict(
    name="AMEX",
    debit_inc=False,
    account_type_id=account_type_name_to_id("Credit Card"),
)

savings: dict = dict(
    name="Chase Savings",
    debit_inc=True,
    account_type_id=account_type_name_to_id("Savings Account"),
)

gas: dict = dict(
    name="Gas for Car",
    debit_inc=True,
    account_type_id=account_type_name_to_id("Gas"),
)

rent: dict = dict(
    name="Apartment Rent",
    debit_inc=True,
    account_type_id=account_type_name_to_id("Rent"),
)

ACCOUNTS: list[dict] = [amex, savings, gas, rent]
