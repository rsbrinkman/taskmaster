import redis
from taskmaster import settings

db = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

def test():
    db.set('test_key', 'test_successful')
    result = db.get('test_key')
    db.delete('test_key')
    return result
