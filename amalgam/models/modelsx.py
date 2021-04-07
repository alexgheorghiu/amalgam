import datetime
from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy import create_engine

"""More details https://docs.sqlalchemy.org/en/14/core/metadata.html """
metadata = MetaData()

users = Table('users', metadata,
              Column('id', Integer, primary_key=True),
              Column('name', String(100), nullable=True),
              Column('email', String(100), nullable=True, unique=True),
              Column('password', String(100), nullable=True))

settings = Table('settings', metadata,
              Column('key', String(100), primary_key=True),
              Column('value', String(256), nullable=True))

sites = Table('sites', metadata,
              Column('id', Integer, primary_key=True),
              Column('name', String(100), nullable=True),
              Column('url', String(2048), nullable=False))

crawls = Table('crawls', metadata,
              Column('id', Integer, primary_key=True),
              Column('date', DateTime, default=datetime.datetime.utcnow),
              Column('note', Text, nullable=True),
              Column('site_id', Integer, ForeignKey(sites.c.id, ondelete="CASCADE")))


class Entity:
    def load_from_rs(self, rs):
        for k,v in rs.items():
            if k not in self.__dict__:
                raise Exception("Property {} not present in object.".format(k))
            self.__dict__[k] = v


class User(Entity):    
    def __init__(self):
        # TODO: Can we add this dynamically from Table? 
        # https://stackoverflow.com/questions/1325673/how-to-add-property-to-a-class-dynamically
        self.id = None
        self.name = None
        self.email = None
        self.password = None

class Setting(Entity):
    def __init__(self):        
        self.key = None
        self.value = None        


class Site(Entity):
    def __init__(self):        
        self.id = None
        self.name = None   
        self.url = None   

class Crawl(Entity):
    def __init__(self, **kwargs):
        self.id = None
        self.date = datetime.datetime.utcnow()
        self.note = None
        self.site_id = None

        for k,v in kwargs.items():
            self.__dict__[k] = v