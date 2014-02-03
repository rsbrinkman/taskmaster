import uuid
import redis
import datetime, time
from taskmaster import settings

db = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

def test():
    db.set('test_key', 'test_successful')
    result = db.get('test_key')
    db.delete('test_key')
    return result

def get_task(taskname):
    return db.hgetall('task>%s' % taskname)

def update_queue_order(orgname, updates):
    db.zadd('org-queues>%s' % orgname, *updates)

def get_org_queues(orgname):
    queues = db.zrange('org-queues>%s' % orgname, 0, -1)

    with db.pipeline() as pipe:
        try:
            pipe.multi()
            for queue in queues:
                pipe.smembers('queue-tasks>%s' % queue)
            queue_tasks = pipe.execute()
        except:
            if settings.DEBUG:
                raise
        finally:
            pipe.reset()

    return zip(queues, (list(tasks) for tasks in queue_tasks))

def get_org_tasks(orgname):
    return db.smembers('org-tasks>%s' % orgname)

def remove_org_task(orgname, task):
    db.srem('org-tasks>%s' % orgname, task)

def get_assigned_tasks(username):
    return db.smembers('assigned>%s' % username)

def assign_task(username, task_id):
    db.sadd('assigned>%s' % username, task_id)

def remove_assigned_task(username, task_id):
    db.srem('assigned>%s' % username, task_id)

def get_tasks_from_tag(tagname):
    return db.smembers('tag-tasks>%s>' % tagname)

def add_task_to_queue(taskname, queuename):
    db.sadd('queue-tasks>%s' % queuename, taskname)

def remove_from_queue(taskname, queuename):
    db.srem('queue-tasks>%s' % queuename, taskname)

def move_task(taskname, from_queuename=None, to_queuename=None):
    if from_queuename and to_queuename:
        db.smove('queue-tasks>%s' % from_queuename, 'queue-tasks>%s' % to_queuename, taskname)
    elif not from_queuename:
        add_task_to_queue(taskname, to_queuename)
    elif not to_queuename:
        remove_from_queue(taskname, from_queuename)

def change_assignee(task_id, current_assignee=None, new_assignee=None):
    if current_assignee and new_assignee:
        db.smove('assigned>%s' % current_assignee, 'assigned>%s' % new_assignee, task_id)
    elif not current_assignee:
        assign_task(new_assignee, task_id)
    elif not new_assignee:
        remove_assigned_task(current_assignee, task_id)

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
            if settings.DEBUG:
                raise
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
            if settings.DEBUG:
                raise
        finally:
            pipe.reset()

def get_used_tags():
    return db.smembers('used-tags')

def create_task(task, orgname):
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
            if task['assignee']:
                pipe.sadd('assigned>%s' % task['assignee'], task_id)
            pipe.execute()
        except:
            if settings.DEBUG:
                raise
        finally:
            pipe.reset()

def update_task(task_id, update_field, update_value):
    if update_field == 'status':
        db.hset('task>%s' % task_id, 'status', update_value)
    elif update_field == 'description':
        db.hset('task>%s' % task_id, 'description', update_value)
    elif update_field == 'queue':
        current_queue = db.hget('task>%s' % task_id, 'queue')
        move_task(task_id, current_queue, update_value)
        db.hset('task>%s' % task_id, 'queue', update_value)
    elif update_field == 'assignee':
        current_assignee = db.hget('task>%s' % task_id, 'assignee')
        change_assignee(task_id, current_assignee, update_value)
        db.hset('task>%s' % task_id, 'assignee', update_value)

def delete_task(task_id, orgname):
    set_tags(task_id, [])
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
            if settings.DEBUG:
                raise
        finally:
            pipe.reset()

def create_queue(name, orgname):
    # Use current epoch time as the score for the sorted set,
    # guarantees that newly added members will be at the end
    score = time.mktime(datetime.datetime.now().timetuple()) * 1000

    # Create the hashmap queue object
    with db.pipeline() as pipe:
        try:
            pipe.multi()
            pipe.zadd('org-queues>%s' % orgname, score, name)
            pipe.execute()
        except:
            if settings.DEBUG:
                raise
        finally:
            pipe.reset()

def delete_queue(name, orgname):
    with db.pipeline() as pipe:
        try:
            pipe.multi()
            pipe.zrem('org-queues>%s' % orgname, name)
            pipe.execute()
        except:
            if settings.DEBUG:
                raise
        finally:
            pipe.reset()

