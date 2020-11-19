from app import db
import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship


# class Site(db.Model):
#     __tablename__ = "sites"
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String, nullable=False)
#     crawls = relationship("Crawl", backref="site")


class Crawl(db.Model):
    __tablename__ = "crawls"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    links = relationship("Link", backref="crawl")


class Link(db.Model):
    __tablename__ = "links"

    id = db.Column(db.Integer, primary_key=True)
    absolute_url = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=True)
    content = db.Column(db.String, nullable=True)
    mime_type = db.Column(db.String, nullable=True)
    crawl_id = db.Column(db.Integer, ForeignKey('crawls.id'))

    def __init__(self, absolute_url, url):
        self.absolute_url = absolute_url
        self.url = url

    def __repr__(self):
        return '<{}={}'.format(self.id, self.absolute_url)