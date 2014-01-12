import redis
from taskmaster import settings

db = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

def test():
    db.set('test_key', 'test_successful')
    result = db.get('test_key')
    db.delete('test_key')
    return result

def get_tasks(task):
    """Get all tasks for a given user.
    task: string task object name for now
    """

    return db.hgetall(task)

def create_task(name, task, username):
    # Create the hashmap task object
    with db.pipeline() as pipe:
        try:
            pipe.multi()
            pipe.hmset('task>%s' % name, task)
            pipe.sadd(username, 'task>%s' % name)
            pipe.execute()
        except:
            print 'Task creation failed'
        finally:
            pipe.reset()


def get_assigned_tasks(username):

    return db.smembers(username)
