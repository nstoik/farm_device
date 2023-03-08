"""Database base configurations."""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

from ..settings import get_config

Base = declarative_base()

config = get_config()  # pylint: disable=invalid-name
engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
db_session = scoped_session(sessionmaker(bind=engine, future=True))


def get_session():
    """Return the sqlalchemy db_session."""

    return db_session


def get_base():
    """Return the sqlalchemy base.

    :version: 0.4
    As of SQLAlchemy 2.0 the query property is considered legacy and the with_query
    parameter was removed.
    """
    return Base


def create_all_tables():
    """Create all tables."""
    base = get_base()
    base.metadata.create_all(bind=engine)


def drop_all_tables():
    """Drop all tables."""
    base = get_base()
    base.metadata.drop_all(bind=engine)
