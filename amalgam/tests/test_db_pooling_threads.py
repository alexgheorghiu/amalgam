"""
Test to see DB connection allocation size while making call from multiple threads
More here:
    https://stackoverflow.com/questions/66938219/sqlalchemy-with-pooling-not-closing-database-connections
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
from sqlalchemy.types import Integer, DateTime, String, Boolean, Text, Float
from sqlalchemy.engine import Engine
from sqlalchemy.pool import NullPool, StaticPool
from sqlalchemy.ext.declarative import declarative_base

# MySQL
SQLALCHEMY_DATABASE = 'mysql'
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://amalgam:amalgam@localhost/amalgam?charset=utf8mb4' # https://stackoverflow.com/questions/47419943/pymysql-warning-1366-incorrect-string-value-xf0-x9f-x98-x8d-t
SQLALCHEMY_ECHO = False
SQLALCHEMY_ENGINE_OPTIONS = {'pool_size': 5, 'max_overflow': 0}
SQLALCHEMY_ISOLATION_LEVEL = "AUTOCOMMIT"

# DB Engine

# engine = create_engine(SQLALCHEMY_DATABASE_URI, 
#                         echo=SQLALCHEMY_ECHO, 
#                         pool_recycle=3600,
#                         isolation_level= SQLALCHEMY_ISOLATION_LEVEL,
#                         **SQLALCHEMY_ENGINE_OPTIONS
#                        ) #  Connect to server

engine = create_engine(SQLALCHEMY_DATABASE_URI, 
                        echo=SQLALCHEMY_ECHO, 
                        # poolclass=NullPool,
                        poolclass=StaticPool,
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
    level = Column(String(100), default=LEVEL_NORMAL)


# Workers


_scoped_session_factory = scoped_session(session_factory)


def single_job(job_id, parent_id):
    session = _scoped_session_factory()

    print("\nSingle Job is: {} -> {}".format(parent_id, job_id))

    user = User(name='User {} {}'.format(job_id, uuid.uuid4()), email='who cares {} {}'.format(job_id, uuid.uuid4()))

    session.add(user)
    session.commit()
    # session.close()

    print("\nSingle Job: {} -> {} done".format(parent_id, job_id))
    sleep(1)
    


def composite_job(job_id):
    print("\nComposite Job is {}".format(job_id))
    NO = 3
    workers = []

    # Create worker threads
    for i in range(NO):
        workers.append(Thread(target=single_job, kwargs={'job_id':i, 'parent_id':job_id}))    

    # Start them
    for worker in workers:
        worker.start()

    # Join them
    for worker in workers:
        worker.join()

    print("\nComposite Job {} done".format(job_id))


CJ_NO = 5
cj_workers = []

# Create worker threads
for i in range(CJ_NO):
    cj_workers.append(Thread(target=composite_job, kwargs={'job_id':i}))    

# Start them
for cj_worker in cj_workers:
    cj_worker.start()

# Join them
for cj_worker in cj_workers:
    cj_worker.join()

# Allow some time to see MySQL's "show processlist;" command
sleep(10)




