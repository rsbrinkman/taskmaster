import datetime
from taskmaster.db import task_model, org_model, queue_model, tags_model
from use_cases import PROJECTS

org = {'name': ''}
queue = {'name': ''}
task = {'name': ''}

try:
    for project in PROJECTS:
        org = org_model.create({
            'name': project['name'],
        })

        for queue_definition in project['queues']:
            queue = queue_model.create({
                'name': queue_definition['name'],
                'org': org['id'],
            })

            for task_id in queue_definition['tasks']:
                task = project['tasks'][task_id]

                task_obj = {
                    "name": task['name'],
                    "org": org['id'],
                    "tags": ','.join(project['tags'].get(task['name'], [])),
                    "status": task.get('status', "Not Started"),
                    "assignee": "",
                    "created_date": datetime.datetime.now().strftime("%Y-%m-%d"),
                    "queue": queue['id'],
                    "description": task['description'],
                }

                created = task_model.create(task_obj)
                tags_model.set(created['id'], 'fake_user_id', project['tags'].get(task_id, []))
except:
    print "Failed on project: %s, queue: %s, task: %s" % (project['name'], queue['name'], task['name'])
