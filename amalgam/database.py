from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

from sqlalchemy.engine import Engine
from sqlalchemy import event


# # SQlite
# SQLALCHEMY_DATABASE = 'sqlite'
# SQLALCHEMY_DATABASE_URI = 'sqlite:///amalgam.db'
# SQLALCHEMY_ECHO = True

# MySQL
SQLALCHEMY_DATABASE = 'mysql'
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://amalgam:amalgam@localhost/amalgam'
SQLALCHEMY_ECHO = False

# Create engine
engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=SQLALCHEMY_ECHO) # connect to server
session_factory = sessionmaker(bind=engine)
Base = declarative_base()

if SQLALCHEMY_DATABASE == 'sqlite':
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """When using SQLite, foreign key support must be enabled explicitly.
        See Foreign Key Support (https://docs.sqlalchemy.org/en/13/dialects/sqlite.html#sqlite-foreign-keys)
        for details."""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

