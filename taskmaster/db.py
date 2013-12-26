import redis
from taskmaster import settings

db = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

def test():
    db.set('test_key', 'test_successful')
    result = db.get('test_key')
    db.delete('test_key')
    return result

def get_tasks(task_name):
    """Get all tasks for a given user.
    hash_name: string task object name for now
    """

    return db.hgetall(task_name)

def create_task(name, task, username):
    # Create the hashmap task object
    try:
        create_task = db.hmset(name, task)
    except:
        print 'Task creation failed'

    # Try Add the task name to the user's assigned set.
    try:
        db.sadd(username, name)
    except:
        print 'whoops'

def get_assigned_tasks(username):

    return db.smembers(username)
