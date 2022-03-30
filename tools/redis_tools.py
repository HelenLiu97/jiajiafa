import json

import redis


class RedisTool(object):
    def __init__(self):

        pool = redis.ConnectionPool(host='localhost', port=6379, db=3, decode_responses=True)
        self.r = redis.Redis(connection_pool=pool)

    def string_set(self, name, value, ex_self=None):
        self.r.set(name, value, ex=ex_self)

    def string_get(self, name):
        return self.r.get(name)

    def string_del(self, name):
        self.r.delete(name)

    def hash_set(self, name, key, value, ):
        self.r.hset(name, key, json.dumps(value))

    def hash_get(self, name, key):
        res = self.r.hget(name, key)
        if not res:
            return None
        return json.loads(res)

    def hash_del(self, name, key):
        res = self.r.hdel(name, key)
        return res


redisTool = RedisTool()
