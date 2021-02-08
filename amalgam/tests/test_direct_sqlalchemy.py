from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy.types import Integer, String

Base = declarative_base()

class Customers(Base):
    __tablename__ = 'customers'
   
    id = Column(Integer, primary_key = True)
    name = Column(String)
    address = Column(String)
    email = Column(String)

engine = create_engine('sqlite:///college.db', echo = True)
conn = engine.connect()

Base.metadata.create_all(engine)