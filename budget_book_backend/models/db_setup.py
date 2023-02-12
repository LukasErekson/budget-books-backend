from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session as sqlaSession

from flask import current_app


class DbSetup:
    """Namespace for database setup functions"""

    engine: Engine = None
    Base = declarative_base()
    Session: sqlaSession = None

    @classmethod
    def set_engine(cls):
        """Set the SQL Alchemy engine according to the given engine_name
        and rebind the session.
        """
        DbSetup.engine = create_engine(current_app.config.get("DATABASE"))
        DbSetup.Session = sessionmaker(bind=DbSetup.engine)

    @classmethod
    def add_tables(cls):
        """Add the tables to the database based on the models that
        inherit from DbSetup.Base.
        """
        DbSetup.Base.metadata.create_all(DbSetup.engine)
