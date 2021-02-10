from sqlalchemy.orm import scoped_session

from amalgam.database import session_factory
from amalgam.models.models import Site, User, Crawl, Link

class Delegate:
    """ 
    Single interface point to the DB

    Links:
        https://stackoverflow.com/questions/6297404/multi-threaded-use-of-sqlalchemy
        https://docs.sqlalchemy.org/en/14/orm/contextual.html 
    """
    def __init__(self, session_factory):        
        self._scoped_session = scoped_session(session_factory)


    def get_session(self):
        return self._scoped_session()        


    def add_tag(self, namestr):
        # session = self.get_session()
        # tag_random = Tag(name=namestr)
        # session.add_all([tag_random])
        # session.commit()
        # print("Tag {} added".format(namestr))
        self._scoped_session.remove()


    def add_user(self, user):
        session = self.get_session()
        session.add_all([user])
        session.commit()


    def create(self, object):
        session = delegate.get_session()
        session.add(object)
        session.commit()

    
    def update(self, object):
        session = delegate.get_session()
        session.commit()


    def delete(self, object):
        session = delegate.get_session()
        session.delete(object)
        session.commit()


    # --------------------------------------------------------------------------

    def crawl_create(self, crawl):
        self.create(crawl)


    def crawl_get_by_id(self, id):
        session = delegate.get_session()
        crawl = session.query(Crawl).get(id) 
        return crawl


    def crawl_get_all(self):
        session = delegate.get_session()
        crawls = session.query(Crawl).all()
        return crawls


    def crawl_delete(self, crawl):
        self.delete(crawl)

    
    def craw_delete_all(self):
        session = self.get_session()
        session.query(Crawl).delete()


    def links_get_for_crawl(self, crawl):
        # session = delegate.get_session()
        # links = session.query(Link).filter
        pass


    def page_create(self, page):
        self.create(page)


    def link_create(self, link):
        self.create(link)


    def link_update(self, link):
        self.update(link)


    def site_create(self, site):
        self.create(site)


    def site_delete_all(self):
        session = self.get_session()
        session.query(Site).delete()
        session.commit()


    def site_get_all(self):
        session = self.get_session()
        return session.query(Site).all()


    def site_get_by_id(self, id):
        session = delegate.get_session()
        site = session.query(Site).get(id)
        session.commit()
        return site


    def site_delete(self, site):
        self.delete(site)

    

# Create and "export" Delegate
delegate = Delegate(session_factory)