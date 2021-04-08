from sqlalchemy.sql import select, update, insert, delete, update
from sqlalchemy import func, or_, desc

from amalgam.database import engine, SQLALCHEMY_DATABASE
from amalgam.models.modelsx import User, users, Site, sites, Crawl, crawls, resources, Resource

class XDelegate:
    def _create(self, table, object):                

        hash = object.__dict__
        if SQLALCHEMY_DATABASE == 'postgresql': # Just skip ID for PostgreSQL (as it complains)
            hash = {}
            for k,v in object.__dict__.items():
                if k == 'id':
                    continue
                
                hash[k] = v
        
        # ins = insert(table).values(object.__dict__)
        ins = insert(table).values(hash)
        conn = engine.connect()
        result = conn.execute(ins)        
        object.id = result.inserted_primary_key[0]
        conn.close()
        return result.inserted_primary_key[0]

    def _update(self, table, object):
        # table.primary_key.columns[0].name
        primarykey_column = table.primary_key.columns[0] # primary key Column
        primarykey_name = primarykey_column.name # # primary key Column's name

        # Prepare the hash (without the primary key pair)
        hash = {}
        for k,v in object.__dict__.items():
            if k == primarykey_name:
                continue            
            hash[k] = v

        up = update(table).values(object.__dict__).where(primarykey_column == object.__dict__[primarykey_name])
        conn = engine.connect()
        result = conn.execute(up)
        conn.close()

    def _get_by_id(self, table, class_name, id):
        conn = engine.connect()
        s = select([table]).where(table.c.id == id)
        rp = conn.execute(s)
        record = rp.first()        
        o = class_name()
        o.load_from_rs(record)
        conn.close()
        return o

    def _get_all(self, table, class_name):
        entities = []
        conn = engine.connect()
        cmd = select([table])
        rp = conn.execute(cmd)
        for record in rp:
            e = class_name()
            e.load_from_rs(record)
            entities.append(e)
        conn.close()
        return entities

    def _delete_all(self, table):
        conn = engine.connect()
        del_cmd = delete(table)
        result = conn.execute(del_cmd)
        conn.close()
        return True if result.rowcount >= 1 else False

    def _delete_by_id(self, table, id):
        conn = engine.connect()
        del_cmd = delete(table).where(table.c.id == id)
        result = conn.execute(del_cmd)
        conn.close()
        return True if result.rowcount >= 1 else False


    def crawl_create(self, crawl):
        return self._create(crawls, crawl)


    def crawl_get_by_id(self, id):
        return self._get_by_id(crawls, Crawl, id)


    def crawl_get_all(self):
        return self._get_all(crawls, Crawl)


    def crawl_get_all_for_site(self, site_id):
        entities = []
        conn = engine.connect()
        cmd = select([crawls]).where(crawls.c.site_id == site_id)
        rp = conn.execute(cmd)
        for record in rp:
            e = Crawl()
            e.load_from_rs(record)
            entities.append(e)
        conn.close()
        return entities

    def crawl_get_last_for_site(self, site_id):
        conn = engine.connect()
        cmd = select([crawls]).where(crawls.c.site_id == site_id).order_by(desc(crawls.c.date))
        record = conn.execute(cmd).first()
        e = Crawl()
        e.load_from_rs(record)
        conn.close()
        return e


    def crawls_and_site(self):
        raise Exception("Not implemented")


    def crawl_delete(self, crawl):
        return self.crawl_delete_by_id(crawl.id)


    def crawl_delete_by_id(self, id):
        return self._delete_by_id(crawls, id)


    def crawl_delete_all(self):
        return self._delete_all(crawls)



    def resource_count_visited(self, crawl_id):
        conn = engine.connect()
        cmd = select([func.count(resources.c.id)])
        record = conn.execute(cmd).first()
        n = record.count_1
        conn.close()
        return n

    def resource_create(self, page):
        return self._create(resources, page)

    def resource_delete_all(self):
        self._delete_all(resources)

    def resource_get_all(self):
        return self._get_all(resources, Resource)

    def resource_get_all_by_crawl(self, crawl_id):
        entities = []
        conn = engine.connect()
        cmd = select([resources]).where(resources.c.crawl_id == crawl_id)
        #.order_by(desc(crawls.c.date))
        rp = conn.execute(cmd)
        for record in rp:
            e = Resource()
            e.load_from_rs(record) 
            entities.append(e)
        conn.close()
        return entities


    def resource_get_by_absolute_url_and_crawl_id(self, absolute_url, crawlId):        
        conn = engine.connect()
        cmd = select([resources]).where(resources.c.crawl_id == crawlId, resources.c.absolute_url == absolute_url)
        #.order_by(desc(crawls.c.date))
        record = conn.execute(cmd).first()        
        if record is None:
            return None
        else:
            e = Resource()
            e.load_from_rs(record) 
            conn.close()
            return e


    def resource_get_by_id(self, resource_id):
        return self._get_by_id(resources, Resource, resource_id)


    def resource_is_present(self, absolute_address, crawlId):
        """Checks to see if a certain Resource is present inside a DB"""
        conn = engine.connect()
        cmd = select([func.count(resources.c.id)]).where(
                        resources.c.absolute_url == absolute_address,
                        resources.c.crawl_id == crawlId)
        record = conn.execute(cmd).first()
        n = record.count_1
        conn.close()
        return n > 0      


    def site_create(self, site):
        return self._create(sites, site)


    def site_update(self, site):
        self._update(sites, site)


    def site_delete_all(self):
        return self._delete_all(sites)


    def site_get_all(self):
        return self._get_all(sites, Site)


    def site_get_by_id(self, id):
        return self._get_by_id(sites, Site, id)


    def site_delete(self, site):
        return self.site_delete_by_id(site.id)


    def site_delete_by_id(self, id):
        conn = engine.connect()
        del_cmd = delete(sites).where(sites.c.id == id)
        result = conn.execute(del_cmd)
        conn.close()
        return True if result.rowcount >= 1 else False


    # def url_create(self, url):
    #     return self._create(urls, url)

    # def url_is_present(self, absolute_address, crawlId):
    #     """Checks to see if a certain absolute address is present inside a DB"""
    #     session = self.get_session()
    #     n = session.query(func.count(Url.id)).filter(Url.absolute_url == absolute_address) \
    #         .filter(Url.crawl_id == crawlId)\
    #         .scalar()
    #     return n > 0

    # def url_update(self, url):
    #     self.update(url)

    # def url_get_by_id(self, id):
    #     session = self.get_session()
    #     crawl = session.query(Url).get(id)
    #     return crawl

    # def url_delete_all(self):
    #     session = self.get_session()
    #     session.query(Url).delete()
    #     session.commit()

    # def url_get_all(self):
    #     session = self.get_session()
    #     urls = session.query(Url).all()
    #     return urls

    # def url_get_all_by_crawl_id(self, crawl_id):
    #     session = self.get_session()
    #     urls = session.query(Url).filter(Url.crawl_id==crawl_id).all()
    #     return urls

    # def url_get_first_unvisited(self, crawl_id):
    #     session = self.get_session()
    #     url = session.query(Url)\
    #         .filter(Url.job_status==Url.JOB_STATUS_NOT_VISITED)\
    #         .filter(Url.type==Url.TYPE_INTERNAL) \
    #         .filter(Url.crawl_id == crawl_id) \
    #         .first()
    #     return url

    # def url_get_all_unvisited(self, crawl_id):
    #     session = self.get_session()
    #     urls = session.query(Url) \
    #         .filter(Url.job_status == Url.JOB_STATUS_NOT_VISITED) \
    #         .filter(Url.type == Url.TYPE_INTERNAL) \
    #         .filter(Url.crawl_id == crawl_id) \
    #         .all()
    #     return urls

    # def url_count_unvisited(self, crawl_id):
    #     """Count unvisited and internal links"""

    #     session = self.get_session()
    #     query = session.query(func.count(Url.id))\
    #         .filter(Url.job_status == Url.JOB_STATUS_NOT_VISITED)\
    #         .filter(Url.type == Url.TYPE_INTERNAL) \
    #         .filter(Url.crawl_id == crawl_id)
    #     # raw = query.compile(engine)
    #     from amalgam.dbutils import literalquery
    #     raw = literalquery(query)
    #     n = query.scalar()
    #     return n


    # def url_count_incoming_for_resource(self, resource_id):
    #     """Counts no of urls that point to page from a different page"""

    #     session = self.get_session()
    #     query = session.query(func.count(Url.id))\
    #         .filter(Url.src_resource_id != None) \
    #         .filter(Url.dst_resource_id == resource_id) \
    #         .filter(Url.type == Url.TYPE_INTERNAL) \
    #     # raw = query.compile(engine)
    #     from amalgam.dbutils import literalquery
    #     raw = literalquery(query)
    #     # print(raw)
    #     n = query.scalar()
    #     return n


    # def url_count_internal_full(self, crawl_id):
    #     """Counts no of internal urls that have both source and destingation resources"""

    #     session = self.get_session()
    #     query = session.query(func.count(Url.id))\
    #         .filter(Url.src_resource_id != None) \
    #         .filter(Url.dst_resource_id != None) \
    #         .filter(Url.type == Url.TYPE_INTERNAL) \
    #         .filter(Url.crawl_id == crawl_id)
        
    #     # raw = query.compile(engine)
    #     from amalgam.dbutils import literalquery
    #     raw = literalquery(query)
    #     # print(raw)
    #     n = query.scalar()
    #     return n

    # def url_count_pending(self, crawl_id):
    #     """Count unvisited and in_progress and internal links"""

    #     session = self.get_session()
    #     query = session.query(func.count(Url.id))\
    #         .filter(or_(Url.job_status == Url.JOB_STATUS_NOT_VISITED, Url.job_status == Url.JOB_STATUS_IN_PROGRESS))\
    #         .filter(Url.type == Url.TYPE_INTERNAL) \
    #         .filter(Url.crawl_id == crawl_id)
    #     # raw = query.compile(engine)
    #     from amalgam.dbutils import literalquery
    #     raw = literalquery(query)
    #     n = query.scalar()
    #     return n

    # def url_count_visited(self, crawl_id):
    #     session = self.get_session()
    #     n = session.query(func.count(Url.id)).filter(Url.job_status == Url.JOB_STATUS_VISITED, Url.type==Url.TYPE_INTERNAL) \
    #         .filter(Url.crawl_id == crawl_id) \
    #         .scalar()
    #     return n

    # def url_count_external(self, crawl_id):
    #     session = self.get_session()
    #     n = session.query(func.count(Url.id)).filter(Url.type==Url.TYPE_EXTERNAL) \
    #         .filter(Url.crawl_id == crawl_id) \
    #         .scalar()
    #     return n

    def user_create(self, user):
        return self._create(users, user)


    def user_get_by_id(self, user_id):
        return self._get_by_id(users, User, user_id)


    def user_get_by_email_and_password(self, email, password):
        conn = engine.connect()
        cmd = select([users]).where(users.c.email == email, users.c.password == password)
        result = conn.execute(cmd)
        user = User()
        user.load_from_rs(result.first())        
        conn.close()
        return user


    def user_update(self, user):
        return self._update(users, user)
    

    def user_get_all(self):
        return self._get_all(users, User)


    def user_delete_all(self):
        return self._delete_all(users)


    def user_delete_by_id(self, user_id):
        return self._delete_by_id(users, user_id)


    

    