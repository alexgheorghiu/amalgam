"""
An attempt to use SQLAlchemy Core instead of ORM reason being that we will need a lot of custom
queries for reports.
"""

from time import sleep
from threading import Thread, current_thread
import uuid

from sqlalchemy.sql import select
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
    conn.close()
    print(result)

def add_user(parent_id, job_id):
    ins = insert(users).values(name='User {} {}'.format(job_id, uuid.uuid4()), email='who cares {} {}'.format(job_id, uuid.uuid4()), password = 'test')
    print("Compiled query: %s" % ins.compile().params)
    conn = engine.connect()
    result = conn.execute(ins)
    conn.close()
    return result.inserted_primary_key

def get_user_all():
    conn = engine.connect()
    s = select([users])
    rp = conn.execute(s)
    results = rp.fetchall()
    conn.close()
    return results

        
reset_users()
print(engine.pool.status())

# -------------------------------------------------------------



def single_job(job_id, parent_id):
    
    print("\nSingle Job is: {} -> {}".format(parent_id, job_id))
    
    add_user(parent_id, job_id)
    print(engine.pool.status())

    users_res = get_user_all()
    print(users_res)

    print("\nSingle Job: {} -> {} done".format(parent_id, job_id))
    sleep(1)
    


def composite_job(job_id):
    print("\nComposite Job is {}".format(job_id))
    NO = 10
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


CJ_NO = 10
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
sleep(5)