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
from sqlalchemy.orm import scoped_session, close_all_sessions

from amalgam.delegate import engine
from amalgam.models.models import Site, User, Crawl, Url, Resource
from amalgam.delegate import Delegate


# MySQL
SQLALCHEMY_DATABASE = 'mysql'
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://amalgam:amalgam@localhost/amalgam?charset=utf8mb4' # https://stackoverflow.com/questions/47419943/pymysql-warning-1366-incorrect-string-value-xf0-x9f-x98-x8d-t
SQLALCHEMY_ECHO = False
SQLALCHEMY_ENGINE_OPTIONS = {'pool_size': 5, 'max_overflow': 0}

SQLALCHEMY_ISOLATION_LEVEL = "AUTOCOMMIT"

# DB Engine
# engine = create_engine(SQLALCHEMY_DATABASE_URI, 
#                         echo=SQLALCHEMY_ECHO, 
#                         # poolclass=NullPool,
#                         poolclass=StaticPool,
#                         # pool_recycle=3600,
#                        isolation_level= SQLALCHEMY_ISOLATION_LEVEL,
#                     #    **SQLALCHEMY_ENGINE_OPTIONS
#                        ) #  Connect to server

session_factory = sessionmaker(bind=engine)
# delegate = Delegate(strategy=Delegate.SESSION_STATEGY_THREAD_ISOLATION, session_object=session_factory)


_scoped_session_factory = scoped_session(session_factory)



def single_job(job_id, parent_id):
    session = _scoped_session_factory()

    print("\nSingle Job is: {} -> {}".format(parent_id, job_id))

    user = User(name='User {} {}'.format(job_id, uuid.uuid4()), email='who cares {} {}'.format(job_id, uuid.uuid4()))

    # delegate.user_create(user)    
    # session.close()

    session.add(user)
    session.commit()

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



# close_all_sessions()

# This will force closing of all opened connections to the DB
engine.dispose()

# Allow some time to see MySQL's "show processlist;" command
sleep(10)




