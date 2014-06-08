import uuid
import json
import redis
import datetime, time
from taskmaster import settings
from taskmaster.db.utils.redis_conn import db, execute_multi, test as test_redis_db
from taskmaster.db.models.task import TaskModel
from taskmaster.db.models.org import OrgModel
from passlib.apps import custom_app_context

task_model = TaskModel()
org_model = OrgModel()

class UserConflict(Exception):
    pass

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

def get_tasks_from_tag(tagname):
    return db.smembers('tag-tasks>%s>' % tagname)

def set_tags(task_id, updated_tags):
    task = task_model.get(task_id)
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
    user['orgs'] = list(org_model.get_for_user(username))

    return user

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

def update_user(username, update_field, update_value):
    if update_field == 'name':
        db.hset('user>%s' % username, 'name', update_value)

def create_queue(name, orgname, overwrite=False):
    db.zadd('org-queues2>%s' % orgname, _default_score(), name)

    if overwrite:
        db.delete('queue-tasks2>%s' % name)

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
