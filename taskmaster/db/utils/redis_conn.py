import redis
import time
import datetime
from taskmaster import settings

db = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

def test():
    db.set('test_key', 'test_successful')
    result = db.get('test_key')
    db.delete('test_key')
    return result

def execute_multi(func):
    with db.pipeline() as pipe:
        try:
            pipe.multi()
            func(pipe)
            return pipe.execute()
        except:
            if settings.DEBUG:
                raise
        finally:
            pipe.reset()

def default_score():
    # Use current epoch time as the score for the sorted set,
    # guarantees that newly added members will be at the end
    return time.mktime(datetime.datetime.now().timetuple()) * 1000
