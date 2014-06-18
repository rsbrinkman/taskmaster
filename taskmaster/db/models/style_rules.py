from taskmaster.db.utils.base_models import CRUDModel
from taskmaster.db.models.task import TaskModel

task_model = TaskModel()

class StyleRules(CRUDModel):
    def get(self, org_id):
        return {
            'style_rules': [
                {
                    'rule': 'status:done',
                    'class': 'striked',
                }
            ]
        }
