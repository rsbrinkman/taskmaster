import uuid
from taskmaster.db import db, user_model, task_model, org_model, queue_model, tags_model

#
# ORGS
#

orgnames = []
for key in db.keys('org>*'):
    orgnames.append(key[len('org>'):])


for orgname in orgnames:
    org_model.create({
        'name': orgname,
    })

#
# USERS
#

valid_emails = []
for key in db.keys('user>*'):
    if 'orgs>' in key:
        continue

    if not '@' in key:
        continue

    valid_emails.append(key[len('user>'):])


for email in valid_emails:
    old_props = db.hgetall('user>%s' % email)

    # Can't user user_model.create here because we don't have the user's
    # original password available
    _id = uuid.uuid4().hex

    db.hmset('user>%s' % _id, {
        'name': old_props['name'],
        'email': email,
        'password_hash': old_props['password_hash'],
    })

    db.set('user-emails>%s' % email, _id)

#
# Add users to orgs
#

for orgname in orgnames:
    new_org_id = org_model.id_from_name(orgname)
    org_member_emails = db.smembers('org>%s' % orgname)

    for email in org_member_emails:
        user_id = user_model.id_from_email(email)
        org_model.add_user(new_org_id, user_id, level='admin')


### Do queues, then tasks, tasks might not need any migrating
### Filters and tags last, should be easy
