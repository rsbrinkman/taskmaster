import redis
from taskmaster import settings

db = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

def test():
    db.set('test_key', 'test_successful')
    result = db.get('test_key')
    db.delete('test_key')
    return result

def get_tasks(hash_name):
    """Get all tasks for a given user.
    hash_name: string task object name for now
    """

    results = db.hgetall(hash_name)

    return results

def create_task(name, task):

    try:
        create_task = db.hmset(name, task)
    except:
        print 'Task creation failed'
