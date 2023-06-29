"""Account Types"""

# Assets
checking_account: dict = dict(
    id=1,
    name="Checking Account",
    group_name="Assets",
)
savings_account: dict = dict(id=2, name="Savings Account", group_name="Assets")
roth_ira: dict = dict(id=3, name="Roth IRA", group_name="Assets")
ASSETS: list[dict] = [checking_account, savings_account, roth_ira]

# Liablities
credit_card: dict = dict(id=4, name="Credit Card", group_name="Liabilities")
LIABILITIES: list[dict] = [credit_card]
# Expenses
EXPENSES: list[dict] = []
for i, expenses_name in enumerate(
    [
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
    ]
):
    EXPENSES.append(
        dict(id=4 + i + 1, name=expenses_name, group_name="Expenses")
    )

# Income
INCOME: list[dict] = []
for i, income_name in enumerate(
    [
        "Paycheck",
        "Credit Card Rewards",
        "Interest Income",
        "Reimbursement",
        "Gifts (Received)",
    ]
):
    INCOME.append(dict(id=i + 1 + 17, name=income_name, group_name="Income"))

# Equity
opening_balance_equity: dict = dict(
    id=23, name="Opening Balance Equity", group_name="Equity"
)
EQUITY: list[dict] = [opening_balance_equity]


ACCOUNT_TYPES: list[dict] = ASSETS + LIABILITIES + EXPENSES + INCOME + EQUITY
