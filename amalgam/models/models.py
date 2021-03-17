import datetime
from sqlalchemy import ForeignKey, Column, Integer, String, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, DateTime, String, Boolean, Text, Float

from amalgam.database import Base


class Mime(Base):
    __tablename__ = "mimes"
    id = Column(Integer, primary_key=True)    
    mime = Column(String(100), nullable=True)


class Setting(Base):
    __tablename__ = "settings"
    key = Column(String(100), primary_key=True)
    value = Column(String(256), nullable=True)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)    
    name = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True, unique=True)
    password = Column(String(100), nullable=True)


class Site(Base):
    __tablename__ = "sites"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    crawls = relationship("Crawl", backref="site", cascade="all, delete")


class Crawl(Base):
    __tablename__ = "crawls"
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.datetime.utcnow)    
    note = Column(Text, nullable=True)
    resources = relationship("Resource", backref="crawl")
    urls = relationship("Url", backref="crawl")
    site_id = Column(Integer, ForeignKey('sites.id', ondelete="CASCADE"))


class Url(Base):
    __tablename__ = "urls"
    # __table_args__ = (UniqueConstraint('crawl_id', 'absolute_url', name='url_unique_in_crawl'),)

    TYPE_EXTERNAL = "external"
    TYPE_INTERNAL = "internal"

    JOB_STATUS_NOT_VISITED = "not visited"
    JOB_STATUS_IN_PROGRESS = "in progress"
    JOB_STATUS_VISITED = "visited"

    id = Column(Integer, primary_key=True)
    url = Column(String(2048), nullable=True)  # The link as it appears on the page
    absolute_url = Column('absolute_url', String(2048), nullable=False) # The absolute URL it resolves
    text = Column(Text)  # Contains the text of the link, if any
    raw_content = Column(Text)  # Contains the raw HTML content of the link, if any
    created_on = Column(DateTime, default=datetime.datetime.utcnow)
    redirects = Column(Text, nullable=True)  # Contains all the redirects
    type = Column(String(20), nullable=True) # external or internal
    status_code = Column(Integer)
    job_status = Column(String(20), default=JOB_STATUS_NOT_VISITED)  # If crawler visited the link or not
    src_resource_id = Column(Integer, ForeignKey('resources.id', ondelete="CASCADE"), nullable=True)  # Source Resource
    dst_resource_id = Column(Integer, ForeignKey('resources.id'), nullable=True)  # Destination Resource
    crawl_id = Column('crawl_id', Integer, ForeignKey('crawls.id', ondelete="CASCADE"))


    # def __init__(self, absolute_url, url, type):
    #     self.absolute_url = absolute_url
    #     self.url = url
    #     self.type = type

    def __repr__(self):
        return '<{}={}'.format(self.id, self.absolute_url)


class Resource(Base):
    __tablename__ = "resources"
    __table_args__ = {'mysql_charset': 'utf8mb4'}
    id = Column(Integer, primary_key=True)
    absolute_url = Column(String(2048), nullable=False)
    created_on = Column(DateTime, default=datetime.datetime.utcnow)
    content = Column(Text, nullable=True)
    elapsed = Column(Float)
    mime_id = Column(Integer, ForeignKey('mimes.id'))
    crawl_id = Column(Integer, ForeignKey('crawls.id', ondelete="CASCADE"))
