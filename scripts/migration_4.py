from taskmaster.db import db

# Delete old keys that aren't hex strings
for key in db.keys('org>*') + db.keys('user>*') + db.keys('queue>*'):
    if len(key) != 32:
        continue

    try:
        int(key, 16)
        db.delete(key)
    except ValueError:
        pass

# Set all orgs to private
for org_key in db.keys('org>*'):
    db.hset(org_key, 'level', 'private')

# Set all users to owners
for key in db.keys('org-admins>*'):
    org_id = key[len('org-admins>'):]
    for user_id in db.smembers(key):
        db.set('user-role>%s>%s' % user_id, org_id, 'owner')

    db.rename(key, 'org-users>%s' % org_id)
