import os
# from amalgam import database

from amalgam import database
from amalgam.delegate import delegate
from amalgam.models.models import User

if __name__ == '__main__':

    db_full_path = os.path.abspath('./amalgam.db')
    if os.path.isfile(db_full_path):
        print("Removing old database: {}".format(db_full_path))
        os.remove(db_full_path)
    else:
        print("No database present at : {}".format(db_full_path))

    #
    # Create all tables if needed
    database.Base.metadata.create_all(database.engine)
    #
    user = User(email='one@foo.com', password='one', name='one')
    delegate.user_create(user)
    print("User is [{}]".format(user.name))
