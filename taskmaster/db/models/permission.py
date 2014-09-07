from taskmaster.db.utils.redis_conn import db

# pylint: disable-msg=R0903
class PermissionTags(object):
    VIEW = 'view'
    EDIT_USER = 'edit_user'
    EDIT_TASK = 'edit_task'
    EDIT_QUEUE = 'edit_queue'
    EDIT_FILTER = 'edit_filter'
    EDIT_ORG = 'edit_org'

# pylint: disable-msg=R0903
class UserRoles(object):
    OWNER = 'owner'
    ADMIN = 'admin'
    EDITOR = 'editor'
    VIEWER = 'viewer'
    ANYONE = ''

    ordered_roles = [OWNER, ADMIN, EDITOR, VIEWER]

# pylint: disable-msg=R0903
class ProjectLevels(object):
    PUBLIC = 'public'
    READONLY = 'readonly'
    PRIVATE = 'private'

DEFAULT_PERMISSIONS = {
    ProjectLevels.PUBLIC: {
        UserRoles.OWNER: ('allow', '*'),
        UserRoles.ADMIN: ('allow', '*'),
        UserRoles.EDITOR: ('deny', {PermissionTags.EDIT_ORG}),
        UserRoles.VIEWER: ('deny', {PermissionTags.EDIT_ORG}),
        UserRoles.ANYONE: ('deny', {PermissionTags.EDIT_ORG}),
    },
    ProjectLevels.READONLY: {
        UserRoles.OWNER: ('allow', '*'),
        UserRoles.ADMIN: ('allow', '*'),
        UserRoles.EDITOR: ('deny', {PermissionTags.EDIT_ORG}),
        UserRoles.VIEWER: ('allow', {PermissionTags.VIEW}),
        UserRoles.ANYONE: ('allow', {PermissionTags.VIEW}),
    },
    ProjectLevels.PRIVATE: {
        UserRoles.OWNER: ('allow', '*'),
        UserRoles.ADMIN: ('allow', '*'),
        UserRoles.EDITOR: ('deny', {PermissionTags.EDIT_ORG}),
        UserRoles.VIEWER: ('allow', {PermissionTags.VIEW}),
        UserRoles.ANYONE: ('deny', '*'),
    },
}

class PermissionModel(object):
    ROLE_KEY = 'user-role>%s>%s'

    def set_role(self, user_id, org_id, role, db_pipe=db):
        db_pipe.set(self.ROLE_KEY % (user_id, org_id), role)

    def get_role(self, user_id, org_id):
        return db.get(self.ROLE_KEY % (user_id, org_id))

    def revoke(self, user_id, org_id, db_pipe=db):
        db_pipe.delete(self.ROLE_KEY % (user_id, org_id))

    def role_gte(self, user_id, org_id, other_role):
        role = self.get_role(user_id, org_id)
        return self.evaluate_role_gte(role, other_role)

    def evaluate_role_gte(self, role, other_role):
        if role == UserRoles.OWNER:
            return True
        elif role == UserRoles.ADMIN:
            return other_role != UserRoles.OWNER
        elif role == UserRoles.EDITOR:
            return other_role != UserRoles.OWNER and other_role != UserRoles.ADMIN
        elif role == UserRoles.VIEWER:
            return other_role == UserRoles.VIEWER or other_role == UserRoles.ANYONE
        elif role == UserRoles.ANYONE:
            return other_role == UserRoles.ANYONE

    def all_tags(self, user_id, org_id):
        tags = [getattr(PermissionTags, a) for a in dir(PermissionTags) if not a.startswith('__')]
        return {tag: self.permitted(user_id, org_id, tag) for tag in tags}

    def all_lte_roles(self, user_id, org_id):
        user_role = self.get_role(user_id, org_id)
        return [r for r in UserRoles.ordered_roles if self.evaluate_role_gte(user_role, r)]

    def permitted(self, user_id, org_id, tag):
        from taskmaster.db.models.org import OrgModel
        org_model = OrgModel()
        org = org_model.get(org_id)
        role = self.get_role(user_id, org_id)
        if not role:
            role = UserRoles.ANYONE

        if org:
            return self._evaluate(org['level'], role, tag, DEFAULT_PERMISSIONS)
        else:
            return False

    def _evaluate(self, project_level, user_role, tag, rule_set):
        permission_type, permitted_tags = rule_set[project_level][user_role]
        tag_matched = (permitted_tags == '*' or tag in permitted_tags)
        return tag_matched if permission_type == 'allow' else not tag_matched
