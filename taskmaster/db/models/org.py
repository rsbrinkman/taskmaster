from taskmaster.db.utils.redis_conn import db
from taskmaster.db.utils.base_models import CRUDModel
from taskmaster.db.models.task import TaskModel
from taskmaster.db.models.permission import PermissionModel, ProjectLevels, UserRoles

task_model = TaskModel()
permission_model = PermissionModel()

class OrgModel(CRUDModel):
    KEY = 'org>%s'
    USERS_KEY = 'org-users>%s'
    USER_ORGS_KEY = 'user>orgs>%s'
    REQUIRED_FIELDS = {'name'}
    UPDATABLE_FIELDS = {'name', 'level'}
    REVERSE_LOOKUPS = {'name'}
    DEFAULTS = {
        'level': ProjectLevels.PRIVATE
    }

    def _post_create(self, db_pipe, org_id, org):
        self.add_user(org_id, org['owner'], role=UserRoles.OWNER, db_pipe=db_pipe)
        del org['owner']

    def add_user(self, org_id, user_id, role=UserRoles.EDITOR, db_pipe=db):
        db_pipe.sadd(self.USERS_KEY % org_id, user_id)
        db_pipe.sadd(self.USER_ORGS_KEY % user_id, org_id)
        permission_model.set_role(user_id, org_id, role)

    def get_users(self, org_id):
        db.smembers(self.USERS_KEY % org_id)

    def has_user(self, org_id, user_id):
        return db.sismember(self.USERS_KEY % org_id, user_id)

    def get_for_user(self, user_id):
        org_ids = db.smembers(self.USER_ORGS_KEY % user_id)
        return [self.get(org_id) for org_id in org_ids]
