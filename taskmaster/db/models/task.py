from taskmaster.db.utils.redis_conn import db, default_score
from taskmaster.db.utils.base_models import CRUDModel

class TaskModel(CRUDModel):
    KEY = 'task>%s'
    QUEUE_TASKS_KEY = 'queue-tasks2>%s'
    ORG_TASKS_KEY = 'org-tasks2>%s'

    REQUIRED_FIELDS = ['name', 'org']
    DEFAULTS = {
        'queue': '',
        'tags': '',
    }

    def _post_create(self, db_pipe, task_id, task):
        self.add_to_org(task['org'], task_id, db_pipe=db_pipe)
        if task['queue']:
            self.add_to_queue(task_id, task['queue'], db_pipe=db_pipe)

    def _post_update_queue(self, db_pipe, task_id, value):
        current_queue = db.hget(self.KEY % task_id, 'queue')
        self.move(task_id, current_queue, value, db_pipe=db_pipe)

    def _post_delete(self, db_pipe, task_id, task):
        self.remove_from_org(task['org'], task_id, db_pipe=db_pipe)

    def move(self, task_id, from_queue=None, to_queue=None, db_pipe=db):
        if from_queue:
            self.remove_from_queue(task_id, from_queue, db_pipe=db_pipe)
        if to_queue:
            self.add_to_queue(task_id, to_queue, db_pipe=db_pipe)

    def add_to_queue(self, task_id, queue_id, db_pipe=db):
        db_pipe.zadd(self.QUEUE_TASKS_KEY % queue_id,  default_score(), task_id)

    def remove_from_queue(self, task_id, queue_id, db_pipe=db):
        db_pipe.zrem(self.QUEUE_TASKS_KEY % queue_id, task_id)

    def update_order(self, org, updates, queue_name='', db_pipe=db):
        if queue_name:
            db_pipe.zadd(self.QUEUE_TASKS_KEY % queue_name, *updates)
        else:
            db_pipe.zadd(self.ORG_TASKS_KEY % org, *updates)

    def get_for_org(self, org):
        return db.zrange(self.ORG_TASKS_KEY % org, 0, -1)

    def add_to_org(self, org, task_id, db_pipe=db):
        db_pipe.zadd(self.ORG_TASKS_KEY % org, default_score(), task_id)

    def remove_from_org(self, org, task_id, db_pipe=db):
        db_pipe.zrem(self.ORG_TASKS_KEY % org, task_id)
