import uuid
from taskmaster.db import db, user_model, task_model, org_model, queue_model

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

user_name_to_id = {}

for email in valid_emails:
    old_props = db.hgetall('user>%s' % email)

    # Can't use user_model.create here because we don't have the user's
    # original password available
    _id = uuid.uuid4().hex

    db.hmset('user>%s' % _id, {
        'name': old_props['name'],
        'email': email,
        'password_hash': old_props['password_hash'],
    })

    db.set('user-emails>%s' % email, _id)

    user_name_to_id[old_props['name']] = _id

#
# ORGS
#
orgnames = []
for key in db.keys('org>*'):
    try:
        # Check it isn't already converted
        int(key, 16)
        continue
    except ValueError:
        orgnames.append(key[len('org>'):])

for orgname in orgnames:
    org = org_model.create({
        'name': orgname,
    })

    # Add users
    org_member_emails = db.smembers('org>%s' % orgname)
    for email in org_member_emails:
        user_id = user_model.id_from('email', email)
        if user_id:
            org_model.add_user(org['id'], user_id, level='admin')

    # Add queues
    org_queue_names = db.zrange('org-queues2>%s' % orgname, 0, -1)
    for queue_name in org_queue_names:
        try:
            # Check it isn't already converted
            int(queue_name, 16)
            continue
        except ValueError:
            pass

        queue = queue_model.create({
            'name': queue_name,
            'org': org['id'],
        })

        # Have tasks reference queue id instead of queue name
        try:
            db.rename('queue-tasks2>%s' % queue_name, 'queue-tasks2>%s' % queue['id'])
        except:
            print "Queue rename failed on %s" % queue_name

        for task_id in db.zrange('queue-tasks2>%s' % queue['id'], 0, -1):
            task_model.update(task_id, 'queue', queue['id'], internal=True)

    # Have tasks reference org id instead of org name
    try:
        db.rename('org-tasks2>%s' % orgname, 'org-tasks2>%s' % org['id'])
    except:
        print "Org rename failed on %s" % orgname
    for task_id in db.zrange('org-tasks2>%s' % org['id'], 0, -1):
        task_model.update(task_id, 'org', org['id'], internal=True)

        task = task_model.get(task_id)

        # Reset assignee
        if 'assignee' in task and task['assignee'] and task['assignee'] in user_name_to_id:
            user_id = user_name_to_id[task['assignee']]
            task_model.update(task_id, 'assignee', user_id, internal=True)
        else:
            task_model.update(task_id, 'assignee', '', internal=True)


        # Reset tags
        for tag in task['tags'].split(','):
            db.zincrby('org-tags>%s' % org['id'], tag, amount=1)
