from flask import g
from taskmaster.db.models.user import UserModel
from taskmaster.db.models.org import OrgModel
from taskmaster.db.models.task import TaskModel
from taskmaster.email import Message, mail, templates

user_model = UserModel()
org_model = OrgModel()
task_model = TaskModel()
BASE_URL = 'taskmaster.jpmunz.com/'
FROM_EMAIL = 'hello@taskmaster.jpmunz.com'

def mediator(event, **kwargs):
    if event == 'signed_up':
        msg = Message(
            "Welcome to Taskmaster", sender=FROM_EMAIL, recipients=[kwargs['email']], html=templates.WELCOME % {
                'base_url': BASE_URL, 'name': kwargs['name']})
        mail.send(msg)
    if event == 'added_to_project':
        org_name = org_model.get(kwargs['project'])
        org_name = org_name['name']
        msg = Message("Added to Project", sender=FROM_EMAIL,
                      recipients=[kwargs['email']], html=templates.ADDED_TO_PROJECT % {'base_url': BASE_URL, 'project': org_name})
        mail.send(msg)
    if event == 'assigned':
        task_name = task_model.get(kwargs['task_id'])
        user = user_model.get(kwargs['user_id'])
        msg = Message("Assigned to Task", sender=FROM_EMAIL,
                      recipients=[user['email']], html=templates.ASSIGNED_TASK % {'base_url': BASE_URL, 'task': task_name['name']})
        mail.send(msg)
    if event == 'status_update':
        task = task_model.get(kwargs['task_id'])
        user = user_model.get(task['assignee'])
        if task['assignee'] == g.user:
            msg = Message("Task Status Updated", sender=FROM_EMAIL,
                          recipients=[user['email']], html=templates.TASK_STATUS_CHANGE % {
                                'base_url': BASE_URL, 'task': task['name'], 'status': task['status']})
            mail.send(msg)
    if event == 'invite':
        org_name = org_model.get(kwargs['org_id'])
        org_name = org_name['name']
        msg = Message("You've Been Invited to Join Taskmaster!", sender=FROM_EMAIL,
                      recipients=[kwargs['email']], html=templates.INVITED % {
                        'base_url': BASE_URL, 'project': org_name, 'email': kwargs['email']})
        mail.send(msg)
