from .db_setup import DbSetup
from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped


class AccountType(DbSetup.Base):
    """ORM for indiviidual account types.

    Each account type has an ID, a name, and a group to which it belongs.
    """

    __tablename__ = "account_types"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True)
    group: Mapped[str] = mapped_column(String(120))
