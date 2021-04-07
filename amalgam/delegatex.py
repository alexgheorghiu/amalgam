from sqlalchemy.sql import select, update, insert, delete, update

from amalgam.database import engine
from amalgam.models.modelsx import User, users, Site, sites

class XDelegate:

    def site_create(self, site):
        ins = insert(sites).values(site.__dict__)
        conn = engine.connect()
        result = conn.execute(ins)        
        site.id = result.inserted_primary_key[0]
        conn.close()
        return result.inserted_primary_key[0]


    def site_update(self, site):
        cmd = update(sites).values(site.__dict__)
        conn = engine.connect()
        result = conn.execute(cmd)
        conn.close()


    def site_delete_all(self):
        conn = engine.connect()
        del_cmd = delete(sites)
        result = conn.execute(del_cmd)
        conn.close()
        return True if result.rowcount >= 1 else False


    def site_get_all(self):
        entities = []
        conn = engine.connect()
        cmd = select([sites])
        rp = conn.execute(cmd)
        for record in rp:
            user = Site()
            user.load_from_rs(record)
            entities.append(user)
        conn.close()
        return entities


    def site_get_by_id(self, id):
        conn = engine.connect()
        s = select([sites]).where(sites.c.id == id)
        rp = conn.execute(s)
        result = rp.first()        
        site = Site()
        site.load_from_rs(result)
        conn.close()
        return site


    def site_delete(self, site):
        return self.site_delete_by_id(site.id)


    def site_delete_by_id(self, id):
        conn = engine.connect()
        del_cmd = delete(sites).where(sites.c.id == id)
        result = conn.execute(del_cmd)
        conn.close()
        return True if result.rowcount >= 1 else False


    def user_create(self, user):
        ins = insert(users).values(user.__dict__)
        print("Compiled query: %s" % ins.compile().params)
        conn = engine.connect()
        result = conn.execute(ins)        
        user.id = result.inserted_primary_key[0]
        conn.close()
        return result.inserted_primary_key[0]


    def user_get_by_id(self, user_id):
        conn = engine.connect()
        s = select([users]).where(users.c.id == user_id)
        rp = conn.execute(s)
        result = rp.first()        
        user = User()
        user.load_from_rs(result)
        conn.close()
        return user


    def user_get_by_email_and_password(self, email, password):
        conn = engine.connect()
        cmd = select([users]).where(users.c.email == email, users.c.password == password)
        result = conn.execute(cmd)
        user = User()
        user.load_from_rs(result.first())        
        conn.close()
        return user


    def user_update(self, user):
        up = update(users).values(user.__dict__)
        conn = engine.connect()
        result = conn.execute(up)
        conn.close()
    

    def user_get_all(self):
        _users = []
        conn = engine.connect()
        cmd = select([users])
        print("Compiled query: %s" % cmd.compile().params)
        rp = conn.execute(cmd)
        for record in rp:
            user = User()
            user.load_from_rs(record)
            _users.append(user)
        conn.close()
        return _users


    def user_delete_all(self):
        conn = engine.connect()
        del_cmd = delete(users)
        result = conn.execute(del_cmd)
        conn.close()
        return True if result.rowcount >= 1 else False


    def user_delete_by_id(self, user_id):
        conn = engine.connect()
        del_cmd = delete(users).where(users.c.id == user_id)
        result = conn.execute(del_cmd)
        conn.close()
        return True if result.rowcount >= 1 else False



    

    