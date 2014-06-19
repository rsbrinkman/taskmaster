class StyleRules(object):
    def get(self, org_id):
        return {
            'style_rules': [
                {
                    'rule': 'status:done',
                    'class': 'striked',
                }
            ]
        }
