from taskmaster.db.utils.redis_conn import db, default_score
from taskmaster.db.utils.base_models import CRUDModel
from taskmaster.db.models.task import TaskModel

task_model = TaskModel()

class QueueModel(CRUDModel):
    KEY = 'task>%s'
    ORG_QUEUES_KEY = 'org-queues2>%s'
    REQUIRED_FIELDS = ['org', 'name']

    def _post_create(self, db_pipe, queue_id, queue):
        db_pipe.zadd(self.ORG_QUEUES_KEY % queue['org'], default_score(), queue_id)
        queue['tasks'] = []

    def _post_delete(self, db_pipe, queue_id, queue):
        db_pipe.zrem(self.ORG_QUEUES_KEY % queue['org'], queue_id)

    def _post_get(self, queue_id):
        return {
            'tasks': task_model.get_for_queue(queue_id)
        }

    def update_order(self, org_id, updates, db_pipe=db):
        db_pipe.zadd(self.ORG_QUEUES_KEY % org_id, *updates)

    def get_for_org(self, org_id):
        queues = db.zrange(self.ORG_QUEUES_KEY % org_id, 0, -1)
        return [self.get(queue_id) for queue_id in queues]
