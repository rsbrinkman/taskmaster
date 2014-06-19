from taskmaster.db.utils.redis_conn import db, execute_multi
from taskmaster.db.models.task import TaskModel

task_model = TaskModel()

class Tags(object):
    ORG_TAGS = "org-tags>%s"

    def set(self, task_id, updated_tags):
        task = task_model.get(task_id)
        current_tags = set(task['tags'].split(','))
        updated_tags = set(updated_tags)

        tags_to_remove = current_tags.difference(updated_tags)
        tags_to_add = updated_tags.difference(current_tags)

        def m(p):
            task_model.update(task_id, 'tags', ','.join(updated_tags), db_pipe=p)

            for tag in tags_to_add:
                p.zincrby(self.ORG_TAGS % task['org'], tag, amount=1)
            for tag in tags_to_remove:
                p.zincrby(self.ORG_TAGS % task['org'], tag, amount=-1)

        execute_multi(m)

    def get_for_org(self, org_id):
        return db.zrangebyscore(self.ORG_TAGS % org_id, 1, '+inf')
