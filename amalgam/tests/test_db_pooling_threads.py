"""
Test to see DB connection allocation size while making call from multiple threads
"""

from time import sleep
from threading import Thread, current_thread

import uuid


from sqlalchemy import func, or_, desc
from sqlalchemy import event
from sqlalchemy import ForeignKey, Column, Integer, String, DateTime, UniqueConstraint
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import relationship
from sqlalchemy.orm import scoped_session, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Integer, DateTime, String, Boolean, Text, Float
from sqlalchemy.engine import Engine
from sqlalchemy.pool import NullPool

# MySQL
SQLALCHEMY_DATABASE = 'mysql'
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://amalgam:amalgam@localhost/amalgam?charset=utf8mb4' # https://stackoverflow.com/questions/47419943/pymysql-warning-1366-incorrect-string-value-xf0-x9f-x98-x8d-t
SQLALCHEMY_ECHO = False
SQLALCHEMY_ENGINE_OPTIONS = {'pool_size': 40, 'max_overflow': 0}
SQLALCHEMY_ISOLATION_LEVEL = "AUTOCOMMIT"

# DB Engine

# engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=SQLALCHEMY_ECHO, pool_recycle=3600,
#                        isolation_level= SQLALCHEMY_ISOLATION_LEVEL,
#                        **SQLALCHEMY_ENGINE_OPTIONS
#                        ) #  Connect to server

engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=SQLALCHEMY_ECHO, 
                        poolclass=NullPool,
                        # pool_recycle=3600,
                       isolation_level= SQLALCHEMY_ISOLATION_LEVEL,
                    #    **SQLALCHEMY_ENGINE_OPTIONS
                       ) #  Connect to server


session_factory = sessionmaker(bind=engine)
Base = declarative_base()

# ORM Entity
class User(Base):

    LEVEL_NORMAL = 'normal'
    LEVEL_ADMIN = 'admin'

    __tablename__ = "users"
    id = Column(Integer, primary_key=True)    
    name = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True, unique=True)
    password = Column(String(100), nullable=True)
    # current_site_id = Column(Integer, ForeignKey('sites.id', ondelete="SET NULL"))
    level = Column(String(100), default=LEVEL_NORMAL)


# Workers
NO = 10
workers = []

def get_session():
    _scoped_session_factory = scoped_session(session_factory)
    return _scoped_session_factory()
    # return session_factory()
    

def user_create(user):
    session = get_session()
    session.add(user)
    session.commit()
    # session.close()


def job(job_id):
    print("Job is {}".format(job_id))
    # my_session = scoped_session(a_session_factory)
    u = User(name='User {} {}'.format(job_id, uuid.uuid4()), email='who cares {} {}'.format(job_id, uuid.uuid4()))
    user_create(u)
    sleep(10)
    

for i in range(NO):
    workers.append(Thread(target=job, kwargs={'job_id':i}))

for worker in workers:
    worker.start()

for worker in workers:
    worker.join()


sleep(10)




