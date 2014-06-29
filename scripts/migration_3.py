from taskmaster.db import db

for key in db.keys('user-emails>*'):
    email = key[len('user-emails>'):]
    db.rename(key, 'email-lookup-user>%s' % email)


for key in db.keys('org-names>*'):
    orgname = key[len('org-names>'):]
    db.rename(key, 'name-lookup-org>%s' % orgname)
