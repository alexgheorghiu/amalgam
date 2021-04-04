from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

from sqlalchemy.engine import Engine
from sqlalchemy import event


# # SQlite
# SQLALCHEMY_DATABASE = 'sqlite'
# SQLALCHEMY_DATABASE_URI = 'sqlite:///amalgam.db'
# SQLALCHEMY_ECHO = False
# SQLALCHEMY_ENGINE_OPTIONS = {}

# MySQL
SQLALCHEMY_DATABASE = 'mysql'
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://amalgam:amalgam@localhost/amalgam?charset=utf8mb4' # https://stackoverflow.com/questions/47419943/pymysql-warning-1366-incorrect-string-value-xf0-x9f-x98-x8d-t
SQLALCHEMY_ECHO = False
SQLALCHEMY_ENGINE_OPTIONS = {'pool_size': 40, 'max_overflow': 0}


# PostgreSQL
# SQLALCHEMY_DATABASE = 'postgresql'
# SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://amalgam:amalgam@localhost/amalgam'
# SQLALCHEMY_ECHO = False
# SQLALCHEMY_ENGINE_OPTIONS = {}


# SQLALCHEMY_ISOLATION_LEVEL = "READ UNCOMMITTED"
SQLALCHEMY_ISOLATION_LEVEL = "AUTOCOMMIT"
""" 
Without this option set the data updated from a thread is not detected by another thread
 @see https://stackoverflow.com/questions/55840220/why-one-thread-cant-not-detect-the-changed-value-updated-by-the-other-thread
"""

# Create engine
engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=SQLALCHEMY_ECHO, pool_recycle=3600,
                       isolation_level= SQLALCHEMY_ISOLATION_LEVEL,
                       **SQLALCHEMY_ENGINE_OPTIONS
                       ) #  Connect to server
session_factory = sessionmaker(bind=engine)


if SQLALCHEMY_DATABASE == 'sqlite':
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """When using SQLite, foreign key support must be enabled explicitly.
        See Foreign Key Support (https://docs.sqlalchemy.org/en/13/dialects/sqlite.html#sqlite-foreign-keys)
        for details."""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

