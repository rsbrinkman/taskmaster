import uuid
from taskmaster.db.utils.redis_conn import db, execute_multi

class MissingRequiredField(Exception):
    def __init__(self, attribute):
        super(MissingRequiredField, self).__init__("Missing required attribute '%s'" % attribute)

class CRUDModel(object):
    KEY = ''
    REQUIRED_FIELDS = []
    DEFAULTS = {}

    def create(self, attributes):
        for required in self.REQUIRED_FIELDS:
            if required not in attributes:
                raise MissingRequiredField(required)

        obj = dict(self.DEFAULTS.items() + attributes.items())
        _id = uuid.uuid4().hex

        def m(p):
            p.hmset(self.KEY % _id, obj)
            self._post_create(p, _id, obj)

        execute_multi(m)

        obj['id'] = _id

        return obj

    def _post_create(self, db_pipe, _id, obj):
        pass

    def get(self, _id):
        obj = db.hgetall(self.KEY % _id)
        obj['id'] = _id
        obj.update(self._post_get(_id))
        return obj

    # pylint: disable-msg=W0613
    def _post_get(self, _id):
        return {}

    def update(self, _id, field, value):
        def m(p):
            p.hset(self.KEY % _id, field, value)
            try:
                getattr(self, '_post_update_%s' % field)(p, _id, value)
            except AttributeError:
                pass

        execute_multi(m)

    def delete(self, _id):
        obj = self.get(_id)
        def m(p):
            p.delete(self.KEY % _id)
            self._post_delete(p, _id, obj)

        execute_multi(m)

    def _post_delete(self, db_pipe, _id, obj):
        pass
