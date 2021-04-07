"""
An attempt to use SQLAlchemy Core instead of ORM

Here are a few reasons to use SQLAlchemy Core instead of ORM
    * ORM has the concept of Session and unit-of-work that makes things very complicated when you want to 
        create objects into a Thread and use them in another or when you create some objects in a method, close
        connection and try to use them in another method (ORM will complain of not being attached to a Session)
    * The syntax for ORM is more far away from SQL than the Core syntax.
    * We will need a lot of custom queries for reports and this mean to load a lot of ORM objesct and then to mix
        and match fields of those objects to generate reports. In Core you simply use SQL (in the worse case scenario)
    * We do not use the ORM relationships too much so there is no need to navigate those relationships - which also
        might be tricky (lazzy loading of them, etc)
"""

from time import sleep
from threading import Thread, current_thread
import uuid

from amalgam.database import engine

from amalgam.models.modelsx import User, metadata
from amalgam.delegatex import XDelegate



def drop_tables():
    """Drop all tables"""
    metadata.drop_all(engine)

    # if database.SQLALCHEMY_DATABASE == 'sqlite':
    #     db_full_path = os.path.abspath('./amalgam.db')
    #     if os.path.isfile(db_full_path):
    #         print("Removing old database: {}".format(db_full_path))
    #         os.remove(db_full_path)
    #     else:
    #         print("No database present at : {}".format(db_full_path))
    # elif database.SQLALCHEMY_DATABASE == 'mysql':
    #     # TODO: Add a drop all table
    #     #  Maybe: https://stackoverflow.com/questions/11233128/how-to-clean-the-database-dropping-all-records-using-sqlalchemy
    #     pass


def create_tables():
    """Create all tables if needed"""
    metadata.create_all(engine)


def empty():
    """Create a clean set of tables"""
    drop_tables()
    create_tables()


# def one():        
#     reset_users()
#     print(engine.pool.status())

#     # -------------------------------------------------------------



#     def single_job(job_id, parent_id):
        
#         print("\nSingle Job is: {} -> {}".format(parent_id, job_id))
        
#         user_id = add_user(parent_id, job_id)
#         print(engine.pool.status())

#         user = user_get_by_id(user_id)
#         print(user)
#         print(type(user['id']))

#         user['email'] = user['email'] + ' la la la'
#         user_update(user)
    
#         print("\nSingle Job: {} -> {} done".format(parent_id, job_id))
#         sleep(1)
        


#     def composite_job(job_id):
#         print("\nComposite Job is {}".format(job_id))
#         NO = 1
#         workers = []

#         # Create worker threads
#         for i in range(NO):
#             workers.append(Thread(target=single_job, kwargs={'job_id':i, 'parent_id':job_id}))    

#         # Start them
#         for worker in workers:
#             worker.start()

#         # Join them
#         for worker in workers:
#             worker.join()

#         print("\nComposite Job {} done".format(job_id))


#     CJ_NO = 1
#     cj_workers = []

#     # Create worker threads
#     for i in range(CJ_NO):
#         cj_workers.append(Thread(target=composite_job, kwargs={'job_id':i}))    

#     # Start them
#     for cj_worker in cj_workers:
#         cj_worker.start()

#     # Join them
#     for cj_worker in cj_workers:
#         cj_worker.join()

#     # Allow some time to see MySQL's "show processlist;" command
#     sleep(5)

def two():
    empty()

    o = {'name': "Alex",  'email':'AEmail', 'password':'Nono no'}

    u = User()
    u.name = 'Zozo'
    print(vars(u))

    u.load_from_rs(o)
    print(vars(u))

    d = XDelegate()
    user_id = d.user_create(u)

    u.id = user_id
    u.name = "Zozox"
    u.email = 'zozo@test.com'
    print(vars(u))
    d.user_update(u)

    u2 = d.user_get_by_id(u.id)
    print(vars(u2))

    rc = d.user_delete_by_id(u2.id)
    print(rc)


if __name__ == '__main__':
    # one()
    two()