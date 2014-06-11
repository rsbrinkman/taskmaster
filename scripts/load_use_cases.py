import datetime
from taskmaster import db
from use_cases import PROJECTS

try:
    for project in PROJECTS:
        db.create_org(project['name'], admin="AUTO_GENERATED", overwrite=True)

        for queue in project['queues']:
            db.create_queue(queue['name'], project['name'], overwrite=True)

            for task_id in queue['tasks']:
                task = project['tasks'][task_id]

                task_obj = {
                    "name": task['name'],
                    "org": project['name'],
                    "tags": ','.join(project['tags'].get(task['name'], [])),
                    "status": task.get('status', "Not Started"),
                    "assignee": "",
                    "created_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                    "queue": queue['name'],
                    "description": task['description'],
                }

                created = db.create_task(task_obj, project['name'])
                db.set_tags(created['id'], project['tags'].get(task_id, []))
except:
    print "Failed on project: %s, queue: %s, task: %s" % (project['name'], queue['name'], task['name'])

