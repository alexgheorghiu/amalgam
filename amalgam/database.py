from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
Base = declarative_base()


engine = create_engine('sqlite:///foo.db')
session_factory = sessionmaker(bind=engine)
