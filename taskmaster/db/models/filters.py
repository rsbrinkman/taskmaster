from taskmaster.db.utils.redis_conn import db, default_score
from taskmaster.db.utils.base_models import CRUDModel

class FilterModel(CRUDModel):
    KEY = 'filter>%s'
    ORG_FILTERS_KEY = 'org-filters>%s'
    REQUIRED_FIELDS = {'name', 'org', 'rule'}
    UPDATABLE_FIELDS = {'name', 'rule'}

    def _post_create(self, db_pipe, filter_id, _filter):
        db_pipe.zadd(self.ORG_FILTERS_KEY % _filter['org'], default_score(), filter_id)

    def _post_delete(self, db_pipe, filter_id, _filter):
        db_pipe.zrem(self.ORG_FILTERS_KEY % _filter['org'], filter_id)

    def get_for_org(self, org, db_pipe=db):
        return db_pipe.zrange(self.ORG_FILTERS_KEY % org, 0, -1)
