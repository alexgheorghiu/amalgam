from sqlalchemy.orm import scoped_session
from sqlalchemy import func, or_, desc

from amalgam.database import session_factory, engine
from amalgam.models.models import Site, User, Crawl, Url, Resource


class Delegate:
    """ 
    Single interface point to the DB

    Links:
        https://stackoverflow.com/questions/6297404/multi-threaded-use-of-sqlalchemy
        https://docs.sqlalchemy.org/en/14/orm/contextual.html 
    """
    SESSION_STATEGY_FIXED = 'fixed'
    SESSION_STATEGY_NEW_ON_DEMAND = 'on demand'
    SESSION_STATEGY_THREAD_ISOLATION = 'on demand isolation'

    strategy = None # "FIXED", "NEW_ON_DEMAND", "THREAD_ISOLATION"

    def __init__(self, strategy = None, session_object=None):
        self.strategy = strategy
        if strategy == Delegate.SESSION_STATEGY_FIXED:
            self._session = session_object
        elif strategy == Delegate.SESSION_STATEGY_FIXED:
            self._session_factory = session_object
        elif strategy == Delegate.SESSION_STATEGY_THREAD_ISOLATION:
            self._session_factory = session_object
            self._scoped_session_factory = scoped_session(session_factory)        
        else:
            raise Exception('Wrong params')

    def get_session(self):
        if self.strategy == Delegate.SESSION_STATEGY_FIXED:
            return self._session
        elif self.strategy == Delegate.SESSION_STATEGY_FIXED:
            return self._session_factory()
        elif self.strategy == Delegate.SESSION_STATEGY_THREAD_ISOLATION:
            return self._scoped_session_factory()



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
        session.add(object)
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

    def crawl_get_all_for_site(self, site_id):
        session = self.get_session()
        return session.query(Crawl)\
            .filter(Crawl.site_id==site_id)\
            .all()

    def crawl_get_last_for_site(self, site_id):
        session = self.get_session()
        return session.query(Crawl)\
            .order_by(desc(Crawl.date))\
            .filter(Crawl.site_id==site_id)\
            .first()


    def crawls_and_site(self):
        session = self.get_session()
        query = session.query(Crawl.id, Site.id, Site.name).join(Site)
        results = query.all()
        for r in results:
            print(r)

    def crawl_delete(self, crawl):
        self.delete(crawl)

    def crawl_delete_all(self):
        session = self.get_session()
        session.query(Crawl).delete()

    # --------------------------------------------------------------------------

    def links_get_for_crawl(self, crawl):
        # session = delegate.get_session()
        # links = session.query(Link).filter
        pass

    def resource_count_visited(self, crawl_id):
        session = self.get_session()
        n = session.query(func.count(Resource.id)) \
            .filter(Resource.crawl_id == crawl_id) \
            .scalar()
        return n

    def resource_create(self, page):
        self.create(page)

    def resource_delete_all(self):
        session = self.get_session()
        session.query(Resource).delete()

    def resource_get_all(self):
        session = self.get_session()
        return session.query(Resource).all()

    def resource_get_all_by_crawl(self, crawl_id):
        session = self.get_session()
        return session.query(Resource)\
            .filter(Resource.crawl_id==crawl_id)\
            .all()

    def resource_get_by_absolute_url_and_crawl_id(self, absolute_url, crawlId):
        session = self.get_session()
        resource = session.query(Resource).filter(Resource.absolute_url == absolute_url, Resource.crawl_id == crawlId).first()
        return resource

    def resource_get_by_id(self, resource_id):
        session = self.get_session()
        return session.query(Resource)\
            .filter(Resource.id==resource_id)\
            .first()

    def resource_is_present(self, absolute_address, crawlId):
        """Checks to see if a certain Resource is present inside a DB"""
        session = self.get_session()
        n = session.query(func.count(Url.id))\
            .filter(Resource.absolute_url == absolute_address)\
            .filter(Resource.crawl_id == crawlId).scalar()
        return n > 0

    def url_create(self, url):
        self.create(url)

    def url_is_present(self, absolute_address, crawlId):
        """Checks to see if a certain absolute address is present inside a DB"""
        session = self.get_session()
        n = session.query(func.count(Url.id)).filter(Url.absolute_url == absolute_address) \
            .filter(Url.crawl_id == crawlId)\
            .scalar()
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

    def url_get_first_unvisited(self, crawl_id):
        session = self.get_session()
        url = session.query(Url)\
            .filter(Url.job_status==Url.JOB_STATUS_NOT_VISITED)\
            .filter(Url.type==Url.TYPE_INTERNAL) \
            .filter(Url.crawl_id == crawl_id) \
            .first()
        return url

    def url_get_all_unvisited(self, crawl_id):
        session = self.get_session()
        urls = session.query(Url) \
            .filter(Url.job_status == Url.JOB_STATUS_NOT_VISITED) \
            .filter(Url.type == Url.TYPE_INTERNAL) \
            .filter(Url.crawl_id == crawl_id) \
            .all()
        return urls

    def url_count_unvisited(self, crawl_id):
        """Count unvisited and internal links"""

        session = self.get_session()
        query = session.query(func.count(Url.id))\
            .filter(Url.job_status == Url.JOB_STATUS_NOT_VISITED)\
            .filter(Url.type == Url.TYPE_INTERNAL) \
            .filter(Url.crawl_id == crawl_id)
        # raw = query.compile(engine)
        from amalgam.dbutils import literalquery
        raw = literalquery(query)
        n = query.scalar()
        return n


    def url_count_incoming_for_resource(self, resource_id):
        """Counts no of urls that point to page from a different page"""

        session = self.get_session()
        query = session.query(func.count(Url.id))\
            .filter(Url.src_resource_id != None) \
            .filter(Url.dst_resource_id == resource_id) \
            .filter(Url.type == Url.TYPE_INTERNAL) \
        # raw = query.compile(engine)
        from amalgam.dbutils import literalquery
        raw = literalquery(query)
        # print(raw)
        n = query.scalar()
        return n


    def url_count_internal_full(self, crawl_id):
        """Counts no of internal urls that have both source and destingation resources"""

        session = self.get_session()
        query = session.query(func.count(Url.id))\
            .filter(Url.src_resource_id != None) \
            .filter(Url.dst_resource_id != None) \
            .filter(Url.type == Url.TYPE_INTERNAL) \
            .filter(Url.crawl_id == crawl_id)
        
        # raw = query.compile(engine)
        from amalgam.dbutils import literalquery
        raw = literalquery(query)
        # print(raw)
        n = query.scalar()
        return n

    def url_count_pending(self, crawl_id):
        """Count unvisited and in_progress and internal links"""

        session = self.get_session()
        query = session.query(func.count(Url.id))\
            .filter(or_(Url.job_status == Url.JOB_STATUS_NOT_VISITED, Url.job_status == Url.JOB_STATUS_IN_PROGRESS))\
            .filter(Url.type == Url.TYPE_INTERNAL) \
            .filter(Url.crawl_id == crawl_id)
        # raw = query.compile(engine)
        from amalgam.dbutils import literalquery
        raw = literalquery(query)
        n = query.scalar()
        return n

    def url_count_visited(self, crawl_id):
        session = self.get_session()
        n = session.query(func.count(Url.id)).filter(Url.job_status == Url.JOB_STATUS_VISITED, Url.type==Url.TYPE_INTERNAL) \
            .filter(Url.crawl_id == crawl_id) \
            .scalar()
        return n

    def url_count_external(self, crawl_id):
        session = self.get_session()
        n = session.query(func.count(Url.id)).filter(Url.type==Url.TYPE_EXTERNAL) \
            .filter(Url.crawl_id == crawl_id) \
            .scalar()
        return n

    def site_create(self, site):
        self.create(site)


    def site_update(self, site):
        self.update(site)

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

    def site_delete_by_id(self, site_id):
        session = self.get_session()
        session.query(Site).filter(Site.id == site_id).delete()
        session.commit()        

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

    def user_update(self, user):
        self.update(user)

    def user_get_all(self):
        session = self.get_session()
        users = session.query(User).all()
        return users

    def user_delete_all(self):
        session = self.get_session()
        session.query(User).delete()
        session.commit()
    
    def user_delete_by_id(self, user_id):
        session = self.get_session()
        session.query(User).filter(User.id == user_id).delete()
        session.commit()


# Create and "export" Delegate
# delegate = Delegate(strategy=Delegate.SESSION_STATEGY_FIXED, session_object=session_factory())
delegate = Delegate(strategy=Delegate.SESSION_STATEGY_THREAD_ISOLATION, session_object=session_factory)
