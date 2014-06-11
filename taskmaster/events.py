from taskmaster import app, emails, settings
from flask import request
import db
import redis
import urllib
from flask_mail import Message
from flask_mail import Mail

mail = Mail(app)
BASE_URL = 'taskmaster.jpmunz.com/'
FROM_EMAIL = 'hello@taskmaster.jpmunz.com'

db = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT)

def mediator(event, **kwargs):
    if event == 'signed_up':
        msg = Message(
            "Welcome to Taskmaster", sender=FROM_EMAIL, recipients=[kwargs['email']], html=emails.WELCOME % {
                'base_url': BASE_URL, 'name': kwargs['name']})
        mail.send(msg)

    if event == 'added_to_project':
        msg = Message("Added to Project", sender=FROM_EMAIL,
                      recipients=[kwargs['email']], html=emails.ADDED_TO_PROJECT % {'base_url': BASE_URL, 'project': kwargs['project']})
        mail.send(msg)
    if event == 'assigned':
        task_name = db.hget('task>%s' % kwargs['task_id'], 'name')
        msg = Message("Assigned to Task", sender=FROM_EMAIL,
                      recipients=[kwargs['email']], html=emails.ASSIGNED_TASK % {'base_url': BASE_URL, 'task': task_name})
        mail.send(msg)
    if event == 'status_update':
        task = db.hgetall('task>%s' % kwargs['task_id'])
        if task['assignee'] == urllib.unquote(request.cookies.get('user', '')):
            msg = Message("Task Status Updated", sender=FROM_EMAIL,
                          recipients=[kwargs['email']], html=emails.TASK_STATUS_CHANGE % {
                                'base_url': BASE_URL, 'task': task['name'], 'status': task['status']})
            mail.send(msg)
    if event == 'invited':
        msg = Message("You've Been Invited to Join Taskmaster!", sender=FROM_EMAIL,
                      recipients=[kwargs['email']], html=emails.INVITED % {
                        'base_url': BASE_URL, 'project': kwargs['org']})
        mail.send(msg)
