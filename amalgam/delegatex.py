from sqlalchemy.sql import select, update, insert, delete, update
from sqlalchemy import func, or_, desc

from amalgam.database import engine, SQLALCHEMY_DATABASE
from amalgam.models.modelsx import User, users, Site, sites, Crawl, crawls

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
        up = update(table).values(object.__dict__)
        conn = engine.connect()
        result = conn.execute(up)
        conn.close()

    def _get_by_id(self, table, class_name, id):
        conn = engine.connect()
        s = select([table]).where(table.c.id == id)
        rp = conn.execute(s)
        result = rp.first()        
        o = class_name()
        o.load_from_rs(result)
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


    

    