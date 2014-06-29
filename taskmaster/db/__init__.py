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
from taskmaster.db.models.filters import FilterModel
from taskmaster.db.utils.base_models import FieldConflict, NotFound, UpdateNotPermitted, InsufficientPermission

task_model = TaskModel()
org_model = OrgModel()
style_rules = StyleRules()
user_model = UserModel()
queue_model = QueueModel()
tags_model = Tags()
filter_model = FilterModel()
