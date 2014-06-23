import uuid
from passlib.apps import custom_app_context
from taskmaster.db.utils.redis_conn import db
from taskmaster.db.utils.base_models import CRUDModel, FieldConflict, NotFound
from taskmaster.db.models.org import OrgModel

org_model = OrgModel()

class UserModel(CRUDModel):
    KEY = 'user>%s'
    ADDRESSES_KEY = 'user-emails>%s'

    REQUIRED_FIELDS = ['name', 'email', 'password']
    DEFAULTS = {}

    def _create(self, db_pipe, user_id, user):
        user['password_hash'] = custom_app_context.encrypt(user['password'])
        del user['password']
        super(UserModel, self)._create(db_pipe, user_id, user)

    def _post_create(self, db_pipe, user_id, user):
        if db.exists(self.ADDRESSES_KEY % user['email']):
            raise FieldConflict("E-mail address", user['email'])

        db_pipe.set(self.ADDRESSES_KEY % user['email'], user_id)
        user['token'] = self._generate_token(user_id, db_pipe=db_pipe)

    def _post_get(self, user_id):
        return {
            'orgs': list(org_model.get_for_user(user_id))
        }

    def _generate_token(self, user_id, db_pipe=None):
        # TODO to do this properly we'll need to
        #   1. set a timeout on the auth token
        #   2. probably reset the timeout every verification
        #   3. do everything over https
        auth_token = uuid.uuid4().hex
        self.update(user_id, 'token', auth_token, db_pipe=db_pipe)

        return auth_token

    def login(self, email, password):
        user_id = self.id_from_email(email)

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
        self.update(user_id, 'token', None)

    def verify_token(self, user_id, provided_token):
        user = self.get(user_id)
        return provided_token and user and user['token'] == provided_token

    def id_from_email(self, email):
        return db.get(self.ADDRESSES_KEY % email)
