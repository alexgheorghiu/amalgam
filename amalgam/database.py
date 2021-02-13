from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

from sqlalchemy.engine import Engine
from sqlalchemy import event

Base = declarative_base()

#TODO: load configuration dynamically 
# engine = create_engine('sqlite:///amalgam.db')
engine = create_engine('sqlite:///amalgam.db', echo=True)
session_factory = sessionmaker(bind=engine)
Base = declarative_base()


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """When using SQLite, foreign key support must be enabled explicitly. 
    See Foreign Key Support (https://docs.sqlalchemy.org/en/13/dialects/sqlite.html#sqlite-foreign-keys) 
    for details."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

