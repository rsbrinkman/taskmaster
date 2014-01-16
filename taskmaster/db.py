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

def get_tasks_from_tag(tagname):
    return db.smembers('tag-tasks>%s>' % tagname)

def add_task_to_queue(taskname, queuename):
    db.sadd('queue-tasks>%s' % queuename, taskname)

def remove_from_queue(taskname, queuename):
    db.srem('queue-tasks>%s' % queuename, taskname)

def move_task(taskname, from_queuename, to_queuename):
    db.smove('queue-tasks>%s' % from_queuename, 'queue-tasks>%s' % to_queuename, taskname)

def set_tags(task_id, updated_tags):
    task = get_task(task_id)
    current_tags = set(task['tags'].split(','))
    updated_tags = set(updated_tags)

    tags_to_remove = current_tags.difference(updated_tags)
    tags_to_add = updated_tags.difference(current_tags)

    task['tags'] = ','.join(updated_tags)

    with db.pipeline() as pipe:
        try:
            pipe.multi()
            for tag in tags_to_remove:
                pipe.srem('tag-tasks>%s' % tag, task_id)
            for tag in tags_to_add:
                pipe.sadd('tag-tasks>%s' % tag, task_id)
                pipe.sadd('used-tags', tag)
            pipe.hmset('task>%s' % task_id, task)
            pipe.execute()
        except:
            print 'Tagging failed'
        finally:
            pipe.reset()

    # Remove any tags that are no longer used
    with db.pipeline() as pipe:
        try:
            pipe.multi()
            for tag in tags_to_remove:
                pipe.scard('tag-tasks>%s' % tag)
            tag_uses = pipe.execute()

            pipe.multi()
            for tag, uses in zip(tags_to_remove, tag_uses):
                if not uses:
                    pipe.srem('used-tags', tag)
            pipe.execute()
        except:
            print 'Tagging failed'
        finally:
            pipe.reset()

def get_used_tags():
    return db.smembers('used-tags')

def remove_tag(taskname, tagname):
    task = get_task(taskname)
    tags = set(task['tags'].split(','))
    try:
        tags.remove(tagname)
    except KeyError:
        pass
    task['tags'] = ','.join(tags)

    with db.pipeline() as pipe:
        try:
            pipe.multi()
            pipe.srem('tag-tasks>%s' % tagname, task)
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
            task['id'] = task_id
            task['tags'] = ''
            pipe.hmset('task>%s' % task_id, task)
            pipe.sadd('org-tasks>%s' % orgname, task_id)
            if username:
                pipe.sadd('assigned>%s' % username, task_id)
            pipe.execute()
        except:
            print 'Task creation failed'
        finally:
            pipe.reset()

def delete_task(task_id, orgname):
    task = get_task(task_id)
    with db.pipeline() as pipe:
        try:
            pipe.multi()
            pipe.delete('task>%s' % task_id)
            pipe.srem('org-tasks>%s' % orgname, task_id)
            if task['assignee']:
                pipe.srem('assigned>%s' % task['assignee'], task_id)
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
