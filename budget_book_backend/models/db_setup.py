from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session as sqlaSession

from os import path
from flask import current_app


class DbSetup:
    """Namespace for database setup functions"""

    engine: Engine
    Base = declarative_base()
    Session: sessionmaker[sqlaSession]

    @classmethod
    def set_engine(cls):
        """Set the SQL Alchemy engine according to the given engine_name
        and rebind the session.
        """
        database_url: str = current_app.config.get(
            "DATABASE",
            "sqlite:///"
            + path.join(
                path.dirname(__file__), "models/databases/database.db"
            ),
        )
        DbSetup.engine = create_engine(database_url, echo=True)
        DbSetup.Session = sessionmaker(bind=DbSetup.engine)

    @classmethod
    def add_tables(cls):
        """Add the tables to the database based on the models that
        inherit from DbSetup.Base.
        """
        DbSetup.Base.metadata.create_all(DbSetup.engine)
