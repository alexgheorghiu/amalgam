from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.pool import NullPool, StaticPool

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
SQLALCHEMY_ENGINE_OPTIONS = {'pool_size': 10, 'max_overflow': 5}


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

# This does persist connnections
# It can maintain a pool of connections alive....just in case :p https://docs.sqlalchemy.org/en/13/core/pooling.html
engine = create_engine(SQLALCHEMY_DATABASE_URI, 
                        echo=SQLALCHEMY_ECHO, 
                        pool_recycle=3600,
                        # poolclass=NullPool,
                        isolation_level= SQLALCHEMY_ISOLATION_LEVEL,
                       **SQLALCHEMY_ENGINE_OPTIONS
                       )

# engine = create_engine(SQLALCHEMY_DATABASE_URI, 
#                         echo=SQLALCHEMY_ECHO, 
#                         pool_recycle=1,
#                         # poolclass=NullPool,
#                         isolation_level= SQLALCHEMY_ISOLATION_LEVEL,
#                        **SQLALCHEMY_ENGINE_OPTIONS
#                        )

# engine = create_engine(SQLALCHEMY_DATABASE_URI, 
#                         echo=SQLALCHEMY_ECHO, 
#                         # pool_recycle=1,
#                         poolclass=NullPool,
#                         isolation_level= SQLALCHEMY_ISOLATION_LEVEL,
#                     #    **SQLALCHEMY_ENGINE_OPTIONS
#                        )

# # Different listeners for Engine events
# @event.listens_for(engine, 'checkout')
# def my_on_checkout(dbapi_conn, connection_rec, connection_proxy):
#     """Called when a connection is retrieved from the Pool."""
#     print("Engine checkout connection")

# @event.listens_for(engine, 'checkin')
# def my_on_checkin(dbapi_conn, connection_rec):
#     """Called when a connection returns to the pool."""
#     print("Engine checkin connection")

# @event.listens_for(engine, 'close')
# def receive_close(dbapi_connection, connection_record):
#     """Called when a DBAPI connection is closed."""
#     print("Engine connection closed")

# @event.listens_for(engine, 'close_detached')
# def receive_close_detached(dbapi_connection):
#     "Called when a detached DBAPI connection is closed."
#     print("Engine detached connection closed")

# @event.listens_for(engine, 'connect')
# def receive_connect(dbapi_connection, connection_record):
#     """Called at the moment a particular DBAPI connection is first created for a given Pool."""
#     print("Engine connection created")


session_factory = sessionmaker(bind=engine)
# scoped_session_factory = scoped_session(session_factory)

def get_session():
    return session_factory()


SESSION_STATEGY_FIXED = 'fixed'
SESSION_STATEGY_NEW_ON_DEMAND = 'on demand'
SESSION_STATEGY_THREAD_ISOLATION = 'on demand isolation'



if SQLALCHEMY_DATABASE == 'sqlite':
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """When using SQLite, foreign key support must be enabled explicitly.
        See Foreign Key Support (https://docs.sqlalchemy.org/en/13/dialects/sqlite.html#sqlite-foreign-keys)
        for details."""
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

