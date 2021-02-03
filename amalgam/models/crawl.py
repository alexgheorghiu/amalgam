import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from amalgam.database import db

class Crawl(db.Model):
    __tablename__ = "crawls"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    links = relationship("Link", backref="crawl")