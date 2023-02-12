# Budget Books Backend Code

## Routes

```python
"""
/api/transactions
-----------------
  GET : Return all the transactions that are associated with the account_id OR all of the given transaction categories.
    (user_id, account_id(s), and/or category_id(s)) => (message: str, transactions:[])

    Example request.json:
    {
      "account_ids": "[1, 2]",
      "user_id": "1"
    }

  POST : Add new transaction(s) to the respective accounts.
    (user_id, transactions:[]) => (message: str)

    Example request.json:
    {
      "user_id": "0",
      "transactions": [
          {
            "name": "Test Post",
            "description": "A Postman test to write to the database.",
            "amount": "50.24",
            "credit_account_id": "1",
            "transaction_date": "2022-10-02"
          }
      ]
    }

  PUT : Categorize the given transaction(s) to their respective category accounts.
    (user_id and transaction_ids and category/account_ids to map them to. Flag whether the category goes into debit or credit. Maybe even tuples?) => (message: str)

    Example request.json:
    {
      "user_id": "0",
      "transactions": [
        {
          "transaction_id": "1",
          "category_id": "1",
          "debit_or_credit": "debit"
        }
      ]
    }

  PATCH : Change existing transaction(s) to have new values.
    (user_id and transaction_ids) => (message: str)

  Example request.json:
  {
      "user_id": "0",
      "transactions": [
          {
            "id": "2",
            "name": "Test Post TWO",
            "description": "A Postman test to write to the database. That has been patched!",
            "amount": "50.24",
            "credit_account_id": "1",
            "transaction_date": "2022-10-03"
          }
      ]
    }

  DELETE : Delete transaction(s) of given id(s).
    (user_id and transaction_ids) => (message: str)

  Example request.json:
  {
    "user_id": "0",
    "transaction_ids": [1, 2]
  }


/api/accounts
-------------
  GET : Return all the accounts that are associated with the user, listing their id, name, balance (as of today), and whether they are a debit increase account or not.
    (user_id, account_type?, balance_start_date?, balance_end_date?) => (message: str, accounts:[])

  Example request.json:
      {
          "user_id": "0",
          "account_type": "bank",
      }

  POST : Add a new account.
    (user_id, account_name, account_type, debit_inc) #=> (message: str)

  Example request.json:
        {
            "user_id": "0",
            "name": "American Express CC",
            "account_type": "Credit Card",
            "debit_inc": false
        }

  PATCH : Update an account's name, type, and whether or not it's a debit increase account.
    (user_id, acount_name, account_type, account_type, debit_inc) => (message: str)

  DELETE : Delete account(s) of given id(s).
    (user_id, account_ids:[]) => (message: str)

"""
```
