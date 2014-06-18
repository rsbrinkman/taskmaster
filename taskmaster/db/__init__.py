import uuid
import json
import redis
import datetime, time
from taskmaster import settings
from taskmaster.db.utils.redis_conn import db, execute_multi, test as test_redis_db
from taskmaster.db.models.task import TaskModel
from taskmaster.db.models.org import OrgModel
from taskmaster.db.models.user import UserModel
from taskmaster.db.models.queue import QueueModel
from taskmaster.db.utils.base_models import FieldConflict, NotFound

task_model = TaskModel()
org_model = OrgModel()
user_model = UserModel()
queue_model = QueueModel()

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
