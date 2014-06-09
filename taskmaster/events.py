from taskmaster import app, emails
from flask_mail import Message
from flask_mail import Mail

mail = Mail(app)
BASE_URL = 'taskmaster.jpmunz.com/'
FROM_EMAIL = 'hello@taskmaster.jpmunz.com'


def mediator(event, email, **kwargs):
    if event == 'signed_up':
        msg = Message(
            "Welcome to Taskmaster", sender=FROM_EMAIL, recipients=[email], html=emails.WELCOME % {
                'base_url': BASE_URL, 'name': kwargs['name']})
        mail.send(msg)

    if event == 'added_to_project':
        msg = Message("Added to Project", sender=FROM_EMAIL,
                      recipients=[email], html=emails.ADDED_TO_PROJECT % {'base_url': BASE_URL, 'project': kwargs['project']})
        mail.send(msg)
    if event == 'assigned':
        msg = Message("Assigned to Task", sender=FROM_EMAIL,
                      recipients=[email], html=emails.ASSIGNED_TASK % {'base_url': BASE_URL, 'task': kwargs['task']})
        mail.send(msg)
    if event == 'status_update':
        msg = Message("Task Status Updated", sender=FROM_EMAIL,
                      recipients=['rsbrinkman@gmail.com'], html=emails.TASK_STATUS_CHANGE % {
                            'base_url': BASE_URL, 'task': kwargs['task'], 'status': kwargs['status']})
        mail.send(msg)
