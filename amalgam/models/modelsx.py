import datetime
from sqlalchemy import MetaData, Table, Column, Integer, Float, String, ForeignKey, DateTime, Text
from sqlalchemy import create_engine

from amalgam.database import SQLALCHEMY_DATABASE

class Entity:
    def __init__(self, **kwargs):
        for k,v in kwargs.items():
            self.__dict__[k] = v

    def load_from_rs(self, rs):
        for k,v in rs.items():
            if k not in self.__dict__:
                raise Exception("Property {} not present in object.".format(k))
            self.__dict__[k] = v


class Mime(Entity):
    def __init__(self, **kwargs):
        self.id = None
        self.mime = None
        super().__init__(**kwargs)


class User(Entity):    
    LEVEL_NORMAL = 'normal'
    LEVEL_ADMIN = 'admin'

    def __init__(self, **kwargs):
        # TODO: Can we add this dynamically from Table? 
        # https://stackoverflow.com/questions/1325673/how-to-add-property-to-a-class-dynamically
        self.id = None
        self.name = None
        self.email = None
        self.password = None
        self.current_site_id = None
        self.level = None
        super().__init__(**kwargs)


class Setting(Entity):
    def __init__(self, **kwargs):        
        self.key = None
        self.value = None        
        super().__init__(**kwargs)


class Site(Entity):
    def __init__(self, **kwargs):        
        self.id = None
        self.name = None   
        self.url = None   
        super().__init__(**kwargs)


class Crawl(Entity):
    def __init__(self, **kwargs):
        self.id = None
        self.date = datetime.datetime.utcnow()
        self.note = None
        self.site_id = None
        super().__init__(**kwargs)


class Url(Entity):
    TYPE_EXTERNAL = "external"
    TYPE_INTERNAL = "internal"

    JOB_STATUS_NOT_VISITED = "not visited"
    JOB_STATUS_IN_PROGRESS = "in progress"
    JOB_STATUS_VISITED = "visited"

    def __init__(self, **kwargs):        
        self.id = None
        self.url = None        
        self.absolute_url = None
        self.text = None
        self.raw_content = None
        self.created_on = datetime.datetime.utcnow()        
        self.redirects = None
        self.type = None
        self.status_code = None
        self.job_status = Url.JOB_STATUS_NOT_VISITED
        self.src_resource_id = None
        self.dst_resource_id = None
        self.crawl_id = None
        super().__init__(**kwargs)



class Resource(Entity):
    def __init__(self, **kwargs):
        self.id = None
        self.absolute_url = None
        self.created_on = None
        self.content = None
        self.elapsed = None
        self.mime_id = None
        self.crawl_id = None
        super().__init__(**kwargs)
        


"""More details https://docs.sqlalchemy.org/en/14/core/metadata.html """
metadata = MetaData()

mimes = Table('mimes', metadata,
              Column('id', Integer, primary_key=True),
              Column('mime', String(100), nullable=True))

users = Table('users', metadata,
              Column('id', Integer, primary_key=True),
              Column('name', String(100), nullable=True),
              Column('email', String(100), nullable=True, unique=True),
              Column('password', String(100), nullable=True),
              Column('current_site_id', Integer, ForeignKey('sites.id', ondelete="SET NULL")),
              Column('level', String(100), default=User.LEVEL_NORMAL))

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

urls = Table('urls', metadata,
              Column('id', Integer, primary_key=True),
              Column('url', String(2048), nullable=True), # The link as it appears on the page
              Column('absolute_url', String(2048), nullable=False), # The absolute URL it resolves
              Column('text', Text), # Contains the text of the link, if any
              Column('raw_content', Text), # Contains the raw HTML content of the link, if any 
              Column('created_on', DateTime, default=datetime.datetime.utcnow),
              Column('redirects', Text, nullable=True), # Contains all the redirects
              Column('type', String(20), nullable=True), # external or internal
              Column('status_code', Integer),
              Column('job_status', String(20), default=Url.JOB_STATUS_NOT_VISITED), # If crawler visited the link or not
              Column('src_resource_id', Integer, ForeignKey('resources.id', ondelete="CASCADE"), nullable=True), # Source Resource
              Column('dst_resource_id', Integer, ForeignKey('resources.id', ondelete="CASCADE"), nullable=True, comment = 'Destination Resource'),  # Destination Resource
              Column('crawl_id', Integer, ForeignKey('crawls.id', ondelete="CASCADE"))
            )

resources = Table('resources', metadata,
              Column('id', Integer, primary_key=True),
              Column('absolute_url', String(2048), nullable=False),
              Column('created_on', DateTime, default=datetime.datetime.utcnow),
              Column('content', Text, nullable=True) if SQLALCHEMY_DATABASE == 'postgresql' else Column('content', Text(1 * 1024 * 1024), nullable=True), # PostgreSQL does not support bounded Text      
              Column('elapsed', Float),
              Column('mime_id', Integer, ForeignKey('mimes.id')),
              Column('crawl_id', Integer, ForeignKey('crawls.id', ondelete="CASCADE"))  
            )
