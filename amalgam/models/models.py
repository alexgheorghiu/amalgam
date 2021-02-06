import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, DateTime, String
from amalgam.database import db

class Mime(db.Model):
    __tablename__ = "mimes"
    id = db.Column(Integer, primary_key=True)    
    mime = db.Column(String, nullable=True)


class Setting(db.Model):
    __tablename__ = "settings"
    key = db.Column(String, primary_key=True)    
    value = db.Column(String, nullable=True)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(Integer, primary_key=True)    
    name = db.Column(String, nullable=True)
    email = db.Column(String, nullable=True)
    password = db.Column(String, nullable=True)


class Site(db.Model):
    __tablename__ = "sites"
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String, nullable=False)    
    crawls = relationship("Crawl", backref="site")


class Crawl(db.Model):
    __tablename__ = "crawls"
    id = db.Column(Integer, primary_key=True)
    date = db.Column(DateTime, default=datetime.datetime.utcnow)    
    note = db.Column(String, nullable=True)
    links = relationship("Link", backref="crawl")
    site_id = db.Column(Integer, ForeignKey('sites.id'))


class Page(db.Model):
    __tablename__ = "pages"
    id = db.Column(Integer, primary_key=True)
    absolute_url = db.Column(String, nullable=False)
    created_on = db.Column(DateTime, default=datetime.datetime.utcnow)
    content = db.Column(String, nullable=True)    
    crawl_id = db.Column(Integer, ForeignKey('crawls.id'))    
    mime_id = db.Column(Integer, ForeignKey('mimes.id'))


class Link(db.Model):
    __tablename__ = "links"

    TYPE_EXTERNAL = "external"
    TYPE_INTERNAL = "internal"

    id = db.Column(Integer, primary_key=True)
    url = db.Column(String, nullable=True)  # The link as it appears on the page
    absolute_url = db.Column(String, nullable=False) # The fabsolute URL it resolves    
    created_on = db.Column(DateTime, default=datetime.datetime.utcnow)
    #content = db.Column(String, nullable=True)
    redirects = db.Column(String, nullable=True) # TODO: Convert to large text / blob
    type = db.Column(String, nullable=True) # external or internal
    # mime_type = db.Column(String, nullable=True)    
    parent_page_id = db.Column(Integer, ForeignKey('pages.id'))
    destination_page_id = db.Column(Integer, ForeignKey('pages.id'))

    def __init__(self, absolute_url, url, type):
        self.absolute_url = absolute_url
        self.url = url
        self.type = type

    def __repr__(self):
        return '<{}={}'.format(self.id, self.absolute_url)


