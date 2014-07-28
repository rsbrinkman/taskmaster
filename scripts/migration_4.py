from taskmaster.db import db

# Delete old keys that aren't hex strings

def delete_old_key(prefix):
    for key in db.keys(prefix + '*'):
        val = key[len(prefix):]

        if '>' in val:
            continue

        try:
            int(val, 16)
            if len(val) != 32:
                db.delete(key)
        except ValueError:
            db.delete(key)

delete_old_key('org>')
delete_old_key('queue>')
delete_old_key('user>')
delete_old_key('user>orgs>')

# Set all orgs to private
for org_key in db.keys('org>*'):
    db.hset(org_key, 'level', 'private')

for key in db.keys('org-admins>*'):
    org_id = key[len('org-admins>'):]
    for user_id in db.smembers(key):
        db.set('user-role>%s>%s' % (user_id, org_id), 'owner')

    db.rename(key, 'org-users>%s' % org_id)
