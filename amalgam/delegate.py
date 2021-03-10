from sqlalchemy.orm import scoped_session
from sqlalchemy import func

from amalgam.database import session_factory
from amalgam.models.models import Site, User, Crawl, Url, Resource


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
        session = self.get_session()
        session.add(object)
        session.commit()

    def update(self, object):
        session = self.get_session()
        session.commit()

    def delete(self, object):
        session = self.get_session()
        session.delete(object)
        session.commit()

    # --------------------------------------------------------------------------

    def crawl_create(self, crawl):
        self.create(crawl)

    def crawl_get_by_id(self, id):
        session = self.get_session()
        crawl = session.query(Crawl).get(id) 
        return crawl

    def crawl_get_all(self):
        session = self.get_session()
        crawls = session.query(Crawl).all()
        return crawls

    def crawl_delete(self, crawl):
        self.delete(crawl)

    def crawl_delete_all(self):
        session = self.get_session()
        session.query(Crawl).delete()

    def links_get_for_crawl(self, crawl):
        # session = delegate.get_session()
        # links = session.query(Link).filter
        pass

    def resource_create(self, page):
        self.create(page)

    def resource_delete_all(self):
        session = self.get_session()
        session.query(Resource).delete()

    def resource_get_all(self):
        session = self.get_session()
        return session.query(Resource).all()

    def resource_get_by_absolute_url_and_crawl_id(self, absolute_url, crawlId):
        session = self.get_session()
        resource = session.query(Resource).filter(Resource.absolute_url == absolute_url, Resource.crawl_id == crawlId).first()
        return resource


    def resource_is_present(self, absolute_address):
        """Checks to see if a certain Resource is present inside a DB"""
        session = self.get_session()
        n = session.query(func.count(Url.id)).filter(Resource.absolute_url == absolute_address).scalar()
        return n > 0

    def url_create(self, url):
        self.create(url)

    def url_is_present(self, absolute_address):
        """Checks to see if a certain absolute address is present inside a DB"""
        session = self.get_session()
        n = session.query(func.count(Url.id)).filter(Url.absolute_url == absolute_address).scalar()
        return n > 0

    def url_update(self, url):
        self.update(url)

    def url_get_by_id(self, id):
        session = self.get_session()
        crawl = session.query(Url).get(id)
        return crawl

    def url_delete_all(self):
        session = self.get_session()
        session.query(Url).delete()
        session.commit()

    def url_get_all(self):
        session = self.get_session()
        urls = session.query(Url).all()
        return urls

    def url_get_all_by_crawl_id(self, crawl_id):
        session = self.get_session()
        urls = session.query(Url).filter(Url.crawl_id==crawl_id).all()
        return urls

    def url_get_first_unvisited(self):
        session = self.get_session()
        url = session.query(Url).filter(Url.visited==False).filter(Url.type==Url.TYPE_INTERNAL).first()
        return url

    def url_count_unvisited(self):
        """Count unvisited and internal links"""
        session = self.get_session()
        n = session.query(func.count(Url.id))\
            .filter(Url.visited==False)\
            .filter(Url.type==Url.TYPE_INTERNAL).scalar()
        return n

    def url_count_visited(self):
        session = self.get_session()
        n = session.query(func.count(Url.id)).filter(Url.visited==True, Url.type==Url.TYPE_INTERNAL).scalar()
        return n

    def url_count_external(self):
        session = self.get_session()
        n = session.query(func.count(Url.id)).filter(Url.type==Url.TYPE_EXTERNAL).scalar()
        return n

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
        session = self.get_session()
        site = session.query(Site).get(id)
        session.commit()
        return site

    def site_delete(self, site):
        self.delete(site)

    def user_create(self, user):
        self.create(user)

    def user_get_by_id(self, id):
        session = self.get_session()
        user = session.query(User).get(id)
        session.commit()
        return user

    def user_get_by_email_and_password(self, email, password):
        session = self.get_session()
        # see https://docs.sqlalchemy.org/en/14/orm/query.html#sqlalchemy.orm.Query.filter
        user = session.query(User).filter(User.email == email, User.password == password).first()
        session.commit()
        return user

    def user_get_all(self, id):
        session = self.get_session()
        users = session.query(User).all()
        return users

    def user_delete_all(self):
        session = self.get_session()
        session.query(User).delete()
        session.commit()


# Create and "export" Delegate
delegate = Delegate(session_factory)
