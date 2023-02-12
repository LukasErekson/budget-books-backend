from sqlalchemy import Column, Integer, String
from models.db_setup import DbSetup


class AccountType(DbSetup.Base):
    """ORM for indiviidual account types.

    Each account type has an ID, a name, and a group to which it belongs.
    """

    __tablename__ = "account_types"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True)
    group = Column(String(120))
