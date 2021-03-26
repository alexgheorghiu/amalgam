import os
import argparse
import sys
# from amalgam import database

from amalgam import database
from amalgam.delegate import delegate
from amalgam.models.models import User, Site


def drop_tables():
    """Drop all tables"""
    database.Base.metadata.drop_all(database.engine)

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
    database.Base.metadata.create_all(database.engine)


def empty():
    """Create a clean set of tables"""
    drop_tables()
    create_tables()


def mock():
    """Creates a pre-populated DB"""
    empty()
    user = User(email='one@foo.com', password='one', name='one')
    delegate.user_create(user)
    print("User is [{}]".format(user.name))

    site = Site(name='One', url='http://one.amalgam.scriptoid.com/a.html')
    delegate.site_create(site)
    print("Site is [{}{}]".format(site.name, site.id))

    site = Site(name='Two', url='http://two.amalgam.scriptoid.com/a.html')
    delegate.site_create(site)
    print("Site is [{}{}]".format(site.name, site.id))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Manage DB")
    parser.add_argument('-a', '--action', type=str, default="init", help='Action', required=True)
    args = parser.parse_args()

    if not args.action:
        print('No action provided')
        sys.exit(1)

    action = args.action

    if action == 'empty':
        empty()
    elif action == 'mock':
        mock()




