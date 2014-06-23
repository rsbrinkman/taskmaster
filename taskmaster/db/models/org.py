from taskmaster.db.utils.redis_conn import db, execute_multi
from taskmaster.db.utils.base_models import CRUDModel
from taskmaster.db.models.task import TaskModel
from taskmaster import app, emails

task_model = TaskModel()

class OrgModel(CRUDModel):
    KEY = 'task>%s'
    ORG_QUEUES_KEY = 'org-queues2>%s'
    ADMINS_KEY = 'org-admins>%s'
    USER_ORGS_KEY = 'user>orgs>%s'
    ORG_NAMES_KEY  = 'org-names>%s'

    # TODO Temporarily allow orgs to be created without owners
    # switch back after properly sandboxed example orgs
    REQUIRED_FIELDS = ['name']

    def _post_create(self, db_pipe, org_id, org):
        if 'owner' in org:
            self.add_user(org_id, org['owner'], level='admin', db_pipe=db_pipe)
        #TODO duplicate name check?
        db_pipe.set(self.ORG_NAMES_KEY % org['name'], org_id)

    def add_user(self, org_id, user_id, level='admin', db_pipe=db):
        if level == 'admin':
                db_pipe.sadd(self.ADMINS_KEY % org_id, user_id)

        db_pipe.sadd(self.USER_ORGS_KEY % user_id, org_id)

    def get_users(self, org_id, level='admin'):
        if level == 'admin':
            return db.smembers(self.ADMINS_KEY % org_id)

    def has_user(self, org_id, user_id):
        return db.sismember(self.ADMINS_KEY % org_id, user_id)

    def get_for_user(self, user_id):
        org_ids = db.smembers(self.USER_ORGS_KEY % user_id)
        return [self.get(org_id) for org_id in org_ids]

    def id_from_name(self, name):
        return db.get(self.ORG_NAMES_KEY % name)

    def add_to_waiting_list(self, email, org_id):
        db.sadd('waiting_list>%s' % email, org_id)
