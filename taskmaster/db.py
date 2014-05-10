import uuid
import json
import redis
import datetime, time
from taskmaster import settings
from passlib.apps import custom_app_context

db = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)


class UserConflict(Exception): pass

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

def get_user_preferences(username):
    '''
    Various user level preferences, hard-coded for now
    '''

    return {
        'style_rules': [
            {
                'rule': 'status:done',
                'class': 'striked',
            }
        ]
    }

def get_saved_filters(username):
    filter_names = db.smembers('user-filters>%s' % username)

    def m(p):
        for filter_name in filter_names:
            p.hgetall('user-filters>%s>%s' % (username, filter_name))

    filters = execute_multi(m)

    return dict(zip(filter_names, filters))

def create_filter(username, filter_name, filter_rule):
    obj = {
        'name': filter_name,
        'rule': filter_rule,
    }

    def m(p):
        p.hmset('user-filters>%s>%s' % (username, filter_name), obj)
        p.sadd('user-filters>%s' % username, filter_name)

    execute_multi(m)

    return obj

def delete_filter(username, filter_name):
    def m(p):
        p.delete('user-filters>%s>%s' % (username, filter_name))
        p.srem('user-filters>%s' % username, filter_name)

    execute_multi(m)

def get_task(taskname):
    return db.hgetall('task>%s' % taskname)

def update_queue_order(orgname, updates):
    db.zadd('org-queues2>%s' % orgname, *updates)

def update_task_order(orgname, updates, queue_name=''):
    if queue_name:
        db.zadd('queue-tasks2>%s' % queue_name, *updates)
    else:
        db.zadd('org-tasks2>%s' % orgname, *updates)

def get_org_queues(orgname):
    queues = db.zrange('org-queues2>%s' % orgname, 0, -1)

    with db.pipeline() as pipe:
        try:
            pipe.multi()
            for queue in queues:
                pipe.zrange('queue-tasks2>%s' % queue, 0, -1)
            queue_tasks = pipe.execute()
        except:
            if settings.DEBUG:
                raise
        finally:
            pipe.reset()

    return zip(queues, (list(tasks) for tasks in queue_tasks))

def get_org_tasks(orgname):
    return db.zrange('org-tasks2>%s' % orgname, 0, -1)

def remove_org_task(orgname, task):
    db.zrem('org-tasks2>%s' % orgname, task)

def get_tasks_from_tag(tagname):
    return db.smembers('tag-tasks>%s>' % tagname)

def add_task_to_queue(taskname, queuename):
    db.zadd('queue-tasks2>%s' % queuename,  _default_score(), taskname)

def remove_from_queue(taskname, queuename):
    db.zrem('queue-tasks2>%s' % queuename, taskname)

def move_task(taskname, from_queuename=None, to_queuename=None):
    if from_queuename and to_queuename:
        add_task_to_queue(taskname, to_queuename)
        remove_from_queue(taskname, from_queuename)
    elif not from_queuename:
        add_task_to_queue(taskname, to_queuename)
    elif not to_queuename:
        remove_from_queue(taskname, from_queuename)

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

def get_user(username):
    user = db.hgetall('user>%s' % username)
    user['orgs'] = list(get_user_orgs(username))

    return user

def create_org(orgname, followers=None, admin=None):
    if admin:
        db.sadd('org>%s' % orgname, admin)
        db.sadd('user>orgs>%s' % admin, orgname)

def get_org(search_string):
    org = db.smembers('org>%s' % search_string)
    if org:
        return search_string
    else:
        return None
def add_user_to_org(orgname, user, level='admin'):
    if level == 'admin':
        db.sadd('org>%s' % orgname, user)

    # Also update user object
    db.sadd('user>orgs>%s' % user, orgname)

def get_org_users(orgname, level='admin'):
    if level == 'admin':

        return db.smembers('org>%s' % orgname)

def get_user_orgs(user, level='admin'):
    if level == 'admin':

        return db.smembers('user>orgs>%s' % user)

def create_user(username, name, password):
    key = 'user>%s' % username

    if db.exists(key):
        raise UserConflict

    user = {
        'name': name,
        'username': username,
        'password_hash': custom_app_context.encrypt(password)
    }

    db.hmset(key, user)

    return _generate_token(username)

def login_user(username, password):
    password_hash = db.hget("user>%s" % username, 'password_hash')

    if password_hash and custom_app_context.verify(password, password_hash):
        return _generate_token(username)

def _generate_token(username):
    # TODO to do this properly we'll need to
    #   1. set a timeout on the auth token
    #   2. probably reset the timeout every verification
    #   3. do everything over https
    auth_token = uuid.uuid4().hex
    db.hset("user>%s" % username, 'token', auth_token)

    return auth_token

def logout_user(username):
    db.hdel("user>%s" % username, 'token')

def verify_token(username, provided_token):
    stored_token = db.hget("user>%s" % username, 'token')
    return stored_token and stored_token == provided_token

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
            pipe.zadd('org-tasks2>%s' % orgname,  _default_score(), task_id)
            if task['queue']:
                add_task_to_queue(task_id, task['queue'])
            pipe.execute()
        except:
            if settings.DEBUG:
                raise
        finally:
            pipe.reset()

    return task

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
        db.hset('task>%s' % task_id, 'assignee', update_value)
    elif update_field == 'name':
        db.hset('task>%s' % task_id, 'name', update_value)

def update_user(username, update_field, update_value):
    if update_field == 'name':
        db.hset('user>%s' % username, 'name', update_value)

def delete_task(task_id, orgname):
    set_tags(task_id, [])
    task = get_task(task_id)
    with db.pipeline() as pipe:
        try:
            pipe.multi()
            pipe.delete('task>%s' % task_id)
            pipe.zrem('org-tasks2>%s' % orgname, task_id)
            pipe.execute()
        except:
            if settings.DEBUG:
                raise
        finally:
            pipe.reset()

def create_queue(name, orgname):
    db.zadd('org-queues2>%s' % orgname, _default_score(), name)

def update_queue(queue_name, update_field, update_value):
    #TODO, need to give queues unique ids like tasks rather than using
    # the queue name, otherwise can't easily update it without breaking
    # references
    pass

def delete_queue(name, orgname):
    db.zrem('org-queues2>%s' % orgname, name)

def _default_score():
    # Use current epoch time as the score for the sorted set,
    # guarantees that newly added members will be at the end
    return time.mktime(datetime.datetime.now().timetuple()) * 1000
