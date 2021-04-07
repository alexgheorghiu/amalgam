from sqlalchemy import MetaData, Table, Column, Integer, String
from sqlalchemy import create_engine


metadata = MetaData()

users = Table('users', metadata,
              Column('id', Integer, primary_key=True),
              Column('name', String(100), nullable=True),
              Column('email', String(100), nullable=True, unique=True),
              Column('password', String(100), nullable=True))

settings = Table('settings', metadata,
              Column('key', String(100), primary_key=True),
              Column('value', String(256), nullable=True))

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