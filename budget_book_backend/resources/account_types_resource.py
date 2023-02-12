import json
import pandas as pd
from typing import Mapping
from flask_restful import Resource
from models.db_setup import DbSetup
from .utils import dict_to_json, endpoint_error_wrapper
from flask import request
from models.account_type import AccountType


class AccountTypeResource(Resource):
    """Resource for interacting with the account model."""

    @endpoint_error_wrapper
    def get(self):
        """Return all the account types, with their names and groups,
        with the requested group type. If no group type is given, it
        returns all of them.

        Request Arguments
        -----------------
            group (str) : (Optional) The group of account_types or
                categories to get. This can be "income", "assets",
                "liabilities", "expenses", etc.

        Example url:
            ?group=liabilities
        """
        group: str = request.args.get("group", "all")

        sql_statement: str = """SELECT * FROM account_types """

        if group != "all":
            sql_statement += f" WHERE \"group\" = '{group}'"

        df: pd.DataFrame = pd.read_sql_query(sql_statement, DbSetup.engine)

        return (
            dict(
                message="SUCCESS",
                account_types=json.dumps(dict_to_json(df.to_dict(), df.index)),
            ),
            200,
        )

    @endpoint_error_wrapper
    def post(self):
        """Add a new account type.

        JSON Parameters
        ---------------
            name (str) : The name of the account type- what it will
                appear as accross the app and on the balance
                sheet/expense report.
            group (str) : The name of the group that it's a part of.

        Example request.json:
        {
            "name": "Credit Union Checking",
            "group": "Assets"
        }
        """
        request_json: Mapping = request.get_json()

        with DbSetup.Session() as session:
            try:
                new_acct_type: AccountType = AccountType(
                    name=request_json["name"], group=request_json["group"]
                )

                session.add(new_acct_type)

                session.commit()

            except Exception as e:
                return (
                    json.dumps(
                        dict(
                            message="There was a problem posting the new account type.",
                            error=str(e),
                        )
                    ),
                    500,
                )

        return (
            json.dumps(
                dict(message="SUCCESS", account_name=request_json["name"])
            ),
            200,
        )
