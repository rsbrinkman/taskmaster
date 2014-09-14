import uuid
from passlib.apps import custom_app_context
from taskmaster.db.utils.base_models import CRUDModel, NotFound
from taskmaster.db.models.org import OrgModel
from taskmaster.db.models.permission import PermissionModel
from taskmaster.db.utils.redis_conn import db

org_model = OrgModel()
permission_model = PermissionModel()

class UserModel(CRUDModel):
    KEY = 'user>%s'
    DEFAULTS = {}
    REQUIRED_FIELDS = {'name', 'email', 'password'}
    UPDATABLE_FIELDS = {'name', 'email'}
    REVERSE_LOOKUPS = {'email'}

    def _create(self, db_pipe, user_id, user):
        user['password_hash'] = custom_app_context.encrypt(user['password'])
        del user['password']
        super(UserModel, self)._create(db_pipe, user_id, user)

    def _post_create(self, db_pipe, user_id, user):
        user['token'] = self._generate_token(user_id, db_pipe=db_pipe)

    def _post_get(self, user_id):
        orgs = list(org_model.get_for_user(user_id))

        for org in orgs:
            org['role'] = permission_model.get_role(user_id, org['id'])

        return {
            'orgs': orgs
        }

    def _generate_token(self, user_id, db_pipe=None):
        # TODO to do this properly we'll need to
        #   1. set a timeout on the auth token
        #   2. probably reset the timeout every verification
        #   3. do everything over https
        auth_token = uuid.uuid4().hex
        self.update(user_id, 'token', auth_token, db_pipe=db_pipe, internal=True)

        return auth_token

    def login(self, email, password):
        user_id = self.id_from('email', email)

        if not user_id:
            raise NotFound

        user = self.get(user_id)
        password_hash = user['password_hash']
        valid_password = password_hash and custom_app_context.verify(password, password_hash)

        if valid_password:
            auth_token = self._generate_token(user_id)
            user['token'] = auth_token
            return user

    def logout(self, user_id):
        self.update(user_id, 'token', None, internal=True)

    def verify_token(self, user_id, provided_token):
        user = self.get(user_id)
        return provided_token and user and user['token'] == provided_token

    def add_to_waiting_list(self, username, org_id, role):
        db.sadd('waiting_list_email>%s' % username, '%s_%s' % (org_id, role))
        db.sadd('waiting_list_org>%s' % org_id, '%s_%s' % (username, role))

    def get_waiting_list_for_email(self, email):
        return db.smembers('waiting_list_email>%s' % email)

    def get_waiting_list_for_org(self, org_id):
        return db.smembers('waiting_list_org>%s' % org_id)

    def remove_from_waiting_list(self, email, org_id):
        removes = []

        for entry in self.get_waiting_list_for_org(org_id):
            if entry.startswith(email):
                removes.append(('waiting_list_org>%s' % org_id, entry))

        for entry in self.get_waiting_list_for_email(email):
            if entry.startswith(org_id):
                removes.append(('waiting_list_email>%s' % email, entry))

        for r in removes:
            db.srem(r[0], r[1])
