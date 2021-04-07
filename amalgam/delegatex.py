from sqlalchemy.sql import select, update, insert, delete, update

from amalgam.database import engine
from amalgam.models.modelsx import User, users

class XDelegate:

    def user_create(self, user):
        ins = insert(users).values(user.__dict__)
        print("Compiled query: %s" % ins.compile().params)
        conn = engine.connect()
        result = conn.execute(ins)        
        user.id = result.inserted_primary_key[0]
        conn.close()
        return result.inserted_primary_key[0]

    def user_update(self, user):
        up = update(users).values(user.__dict__)
        conn = engine.connect()
        result = conn.execute(up)
        conn.close()

    def user_get_by_id(self, user_id):
        conn = engine.connect()
        s = select([users]).where(users.c.id == user_id)
        rp = conn.execute(s)
        result = rp.first()        
        user = User()
        user.load_from_rs(result)
        conn.close()
        return user

    def user_delete_by_id(self, user_id):
        conn = engine.connect()
        del_cmd = delete(users).where(users.c.id == user_id)
        result = conn.execute(del_cmd)
        conn.close()
        return True if result.rowcount >= 1 else False

    def user_get_by_email_and_password(self, email, password):
        conn = engine.connect()
        cmd = select([users]).where(users.c.email == email, users.c.password == password)
        result = conn.execute(cmd)
        user = User()
        user.load_from_rs(result.first())        
        conn.close()
        return user

    def user_delete_all(self):
        conn = engine.connect()
        del_cmd = delete(users)
        result = conn.execute(del_cmd)
        conn.close()
        return True if result.rowcount >= 1 else False

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