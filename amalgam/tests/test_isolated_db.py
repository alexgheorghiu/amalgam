"""
See how difficult would be to have the DB completelly idependent from Flask engine

Based on https://gist.github.com/DmitryBe/805fb35e3472b8985c654c8dfb8aa127


https://stackoverflow.com/questions/6297404/multi-threaded-use-of-sqlalchemy
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from datetime import datetime, timedelta
from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session


import threading

import string
import random

def random_string(n=10):
    """Based on https://www.educative.io/edpresso/how-to-generate-a-random-string-in-python"""    
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(10))

Base = declarative_base()

class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    
    def __repr__(self):
        return "<Tag (name='%s')>" % (self.name)

# connection
engine = create_engine('sqlite:///foo.db')

# create metadata
Base.metadata.create_all(engine)

# create session
session_factory = sessionmaker(bind=engine)
# session = session_factory()
Session = scoped_session(session_factory)

# session = Session()


# insert data
# tag_cool = Tag(name='cool')
# tag_car = Tag(name='car')
# tag_animal = Tag(name='animal')

# session.add_all([tag_animal, tag_car, tag_cool])
# session.commit()

# query data
# t1 = session.query(Tag).filter(Tag.name == 'cool').first()

# update entity
# t1.name = 'cool-up'
# session.commit()

# delete
# session.delete(t1)
# session.commit()

class Delegate:
    """ 
    Single interface point to the DB

    Links:
        https://stackoverflow.com/questions/6297404/multi-threaded-use-of-sqlalchemy
        https://docs.sqlalchemy.org/en/14/orm/contextual.html 
    """
    def __init__(self, session_factory):        
        self._scoped_session = scoped_session(session_factory)


    def get_session(self):
        return self._scoped_session()        


    def add_tag(self, namestr):
        session = self.get_session()
        tag_random = Tag(name=namestr)
        session.add_all([tag_random])
        session.commit()
        print("Tag {} added".format(namestr))
        self._scoped_session.remove()



d = Delegate(Session)


def add_random_tag():
    # session = Session()

    while True:
        name = random_string()
        # tag_random = Tag(name='random {}'.format(random_string()))
        # session.add_all([tag_random])
        # session.commit()
        d.add_tag(name)

t1 = threading.Thread(target=add_random_tag)
t2 = threading.Thread(target=add_random_tag)

t1.start()
t2.start()

t1.join()
t2.join()
