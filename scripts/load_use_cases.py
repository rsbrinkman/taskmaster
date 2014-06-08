import datetime
from taskmaster import db
from taskmaster.db import task_model, org_model
from use_cases import PROJECTS

try:
    for project in PROJECTS:
        org = org_model.create({
            'name': project['name'],
            'owner': "AUTO_GENERATED",
        })

        for queue in project['queues']:
            db.create_queue(queue['name'], org['id'], overwrite=True)

            for task_id in queue['tasks']:
                task = project['tasks'][task_id]

                task_obj = {
                    "name": task['name'],
                    "org": org['id'],
                    "tags": ','.join(project['tags'].get(task['name'], [])),
                    "status": task.get('status', "Not Started"),
                    "assignee": "",
                    "created_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                    "queue": queue['name'],
                    "description": task['description'],
                }

                created = task_model.create(task_obj)
                db.set_tags(created['id'], project['tags'].get(task_id, []))
except:
    print "Failed on project: %s, queue: %s, task: %s" % (project['name'], queue['name'], task['name'])

