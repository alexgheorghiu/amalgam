from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

Base = declarative_base()

#TODO: load configuration dynamically 
engine = create_engine('sqlite:///amalgam.db')
session_factory = sessionmaker(bind=engine)
Base = declarative_base()


