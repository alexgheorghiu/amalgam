import datetime
from sqlalchemy import ForeignKey, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, DateTime, String

from amalgam.database import Base, engine


class Mime(Base):
    __tablename__ = "mimes"
    id = Column(Integer, primary_key=True)    
    mime = Column(String, nullable=True)


class Setting(Base):
    __tablename__ = "settings"
    key = Column(String, primary_key=True)    
    value = Column(String, nullable=True)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)    
    name = Column(String, nullable=True)
    email = Column(String, nullable=True, unique=True)
    password = Column(String, nullable=True)


class Site(Base):
    __tablename__ = "sites"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)    
    crawls = relationship("Crawl", backref="site", cascade="all, delete")


class Crawl(Base):
    __tablename__ = "crawls"
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.datetime.utcnow)    
    note = Column(String, nullable=True)
    pages = relationship("Page", backref="crawl")
    links = relationship("Link", backref="crawl")
    site_id = Column(Integer, ForeignKey('sites.id', ondelete="CASCADE"))


class Link(Base):
    __tablename__ = "links"

    TYPE_EXTERNAL = "external"
    TYPE_INTERNAL = "internal"

    id = Column(Integer, primary_key=True)
    url = Column(String, nullable=True)  # The link as it appears on the page
    absolute_url = Column(String, nullable=False) # The fabsolute URL it resolves    
    created_on = Column(DateTime, default=datetime.datetime.utcnow)
    redirects = Column(String, nullable=True) # TODO: Convert to large text / blob
    type = Column(String, nullable=True) # external or internal
    parent_page_id = Column(Integer, ForeignKey('pages.id', ondelete="CASCADE"), nullable=True)
    destination_page_id = Column(Integer, ForeignKey('pages.id'), nullable=True)
    crawl_id = Column(Integer, ForeignKey('crawls.id', ondelete="CASCADE"))

    # def __init__(self, absolute_url, url, type):
    #     self.absolute_url = absolute_url
    #     self.url = url
    #     self.type = type

    def __repr__(self):
        return '<{}={}'.format(self.id, self.absolute_url)


class Page(Base):
    __tablename__ = "pages"
    id = Column(Integer, primary_key=True)
    absolute_url = Column(String, nullable=False)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)
    content = Column(String, nullable=True)
    mime_id = Column(Integer, ForeignKey('mimes.id'))
    crawl_id = Column(Integer, ForeignKey('crawls.id', ondelete="CASCADE"))
