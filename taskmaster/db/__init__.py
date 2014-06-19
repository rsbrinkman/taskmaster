import uuid
import json
import redis
import datetime, time
from taskmaster import settings
from taskmaster.db.utils.redis_conn import db, execute_multi, test as test_redis_db
from taskmaster.db.models.task import TaskModel
from taskmaster.db.models.org import OrgModel
from taskmaster.db.models.style_rules import StyleRules
from taskmaster.db.models.user import UserModel
from taskmaster.db.models.queue import QueueModel
from taskmaster.db.models.tags import Tags
from taskmaster.db.utils.base_models import FieldConflict, NotFound

task_model = TaskModel()
org_model = OrgModel()
style_rules = StyleRules()
user_model = UserModel()
queue_model = QueueModel()
tags_model = Tags()

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
