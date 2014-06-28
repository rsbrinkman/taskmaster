from taskmaster.db import db

for key in db.keys('org-admins>*'):
    org_id = key[len('user-emails>'):]
    db.rename(key, 'org-users>%s' % org_id)
