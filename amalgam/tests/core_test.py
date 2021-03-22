"""
An attempt to use SQLAlchemy Core instead of ORM reason being that we will need a lot of custom
queries for reports.
"""
from sqlalchemy.orm import scoped_session
from sqlalchemy import MetaData, Table, Column, Integer, String, insert, delete
from sqlalchemy import create_engine

from amalgam.database import session_factory, engine


metadata = MetaData()
#
users = Table('users', metadata,
              Column('id', Integer, primary_key=True),
              Column('name', String(100), nullable=True),
              Column('email', String(100), nullable=True, unique=True),
              Column('password', String(100), nullable=True))
#
# metadata.create_all(engine)

def reset_users():
    conn = engine.connect()
    deletion = delete(users)
    result = conn.execute(deletion)
    print(result)

def add_user():
    ins = insert(users).values(name='alex', email = 'alex@scriptoid.com', password = 'test')
    print("Compiled query: %s" % ins.compile().params)
    conn = engine.connect()
    result = conn.execute(ins)
    return result.inserted_primary_key
    con.close()


reset_users()
print(add_user())
