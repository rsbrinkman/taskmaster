import json
import uuid
from taskmaster.db.utils.redis_conn import db, execute_multi

class NotFound(Exception):
    pass

class InsufficientPermission(Exception):
    def __init__(self):
        super(InsufficientPermission, self).__init__('You are not authorized to perform this action')

class UpdateNotPermitted(Exception):
    def __init__(self, field):
        super(UpdateNotPermitted, self).__init__('%s cannot be updated externally' % field)

class FieldConflict(Exception):
    def __init__(self, field, value):
        super(FieldConflict, self).__init__("%s '%s' is already in use" % (field, value))

class MissingRequiredField(Exception):
    def __init__(self, attribute):
        super(MissingRequiredField, self).__init__("Missing required attribute '%s'" % attribute)

class CRUDModel(object):
    KEY = ''
    REQUIRED_FIELDS = []
    DEFAULTS = {}
    PARAMS_TO_ENCODE = set([])
    UPDATABLE_FIELDS = set([])

    def create(self, attributes, db_pipe=None):
        for required in self.REQUIRED_FIELDS:
            if required not in attributes:
                raise MissingRequiredField(required)

        obj = dict(self.DEFAULTS.items() + attributes.items())
        _id = uuid.uuid4().hex

        for p in self.PARAMS_TO_ENCODE:
            obj[p] = json.dumps(obj[p])

        def m(p):
            self._create(p, _id, obj)
            self._post_create(p, _id, obj)

        if db_pipe:
            m(db_pipe)
        else:
            execute_multi(m)

        obj['id'] = _id


        return obj

    def _create(self, db_pipe, _id, obj):
        db_pipe.hmset(self.KEY % _id, obj)

    def _post_create(self, db_pipe, _id, obj):
        pass

    def get(self, _id, include=None):
        obj = db.hgetall(self.KEY % _id)
        if obj:
            obj['id'] = _id
            obj.update(self._post_get(_id))

            for p in self.PARAMS_TO_ENCODE:
                obj[p] = json.loads(obj[p])

            if include:
                obj = { k: obj[k] for k in include }

            return obj

    # pylint: disable-msg=W0613
    def _post_get(self, _id):
        return {}

    def update(self, _id, field, value, db_pipe=None, internal=False):
        if not (internal or field in self.UPDATABLE_FIELDS):
            raise UpdateNotPermitted(field)

        if value in self.PARAMS_TO_ENCODE:
            value = json.dumps(value)

        def m(p):
            p.hset(self.KEY % _id, field, value)
            try:
                getattr(self, '_post_update_%s' % field)(p, _id, value)
            except AttributeError:
                pass

        if db_pipe:
            m(db_pipe)
        else:
            execute_multi(m)

    def delete(self, _id, db_pipe=None):
        obj = self.get(_id)
        def m(p):
            p.delete(self.KEY % _id)
            self._post_delete(p, _id, obj)

        if db_pipe:
            m(db_pipe)
        else:
            execute_multi(m)

    def _post_delete(self, db_pipe, _id, obj):
        pass
