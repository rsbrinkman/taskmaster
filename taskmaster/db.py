import uuid
import redis
from datetime import datetime
from taskmaster import settings

db = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

def test():
    db.set('test_key', 'test_successful')
    result = db.get('test_key')
    db.delete('test_key')
    return result

def get_task(taskname):
    return db.hgetall('task>%s' % taskname)

def get_queue(queuename):
    return db.hgetall('queue>%s' % queuename)

def get_queue_tasks(queuename):
    return db.smembers('queue-tasks>%s' % queuename)

def get_org_queues(orgname):
    return db.smembers('org-queues>%s' % orgname)

def get_org_tasks(orgname):
    return db.smembers('org-tasks>%s' % orgname)

def get_assigned_tasks(username):
    return db.smembers('assigned>%s' % username)

def get_tasks_from_tag(tagname, orgname):
    return db.smembers('tag-tasks>%s>' % tagname)

def remove_tag(taskname, tagname):
    pass

def remove_from_queue(taskname, queuename):
    pass

def move_task(taskname, from_queuename, to_queuename):
    pass

def delete_task(taskname):
    pass

def add_task_to_queue(taskname, queuename):
    db.sadd('queue-tasks>%s' % queuename, taskname)

def tag_task(taskname, tagname):
    task = get_task(taskname)
    tags = set(task['tags'].split(','))
    tags.add(tagname)
    task['tags'] = ','.join(tags)
    orgname = task['org']

    with db.pipeline() as pipe:
        try:
            pipe.multi()
            pipe.sadd('tag-tasks>%s' % tagname, task)
            pipe.hmset('task>%s' % taskname, task)
            pipe.execute()
        except:
            print 'Task creation failed'
        finally:
            pipe.reset()

def create_task(task, orgname, username=None):
    # Create the hashmap task object
    task_id = uuid.uuid4().hex
    with db.pipeline() as pipe:
        try:
            pipe.multi()
            task['org'] = orgname
            pipe.hmset('task>%s' % task_id, task)
            pipe.sadd('org-tasks>%s' % orgname, task_id)
            if username:
                pipe.sadd('assigned>%s' % username, task_id)
            pipe.execute()
        except:
            print 'Task creation failed'
        finally:
            pipe.reset()

def create_queue(name, orgname, filter_expression=None):
    # Create the hashmap queue object
    with db.pipeline() as pipe:
        try:
            pipe.multi()
            pipe.hmset('queue>%s' % name, {
                'created': str(datetime.now().replace(microsecond=0)),
                'filter_expression': filter_expression,
            })
            pipe.sadd('org-queues>%s' % orgname, name)
            pipe.execute()
        except:
            print 'Task creation failed'
        finally:
            pipe.reset()

