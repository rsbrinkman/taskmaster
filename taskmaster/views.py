import json

from taskmaster import app, db
from flask import render_template, request, Response
from datetime import datetime

#TODO: Create login interface.
org='Taskmaster'
username='Scott Brinkman'

@app.route('/')
def index():
    # Get set of assigned tasks
    assigned_tasks = db.get_assigned_tasks(username)
    # Iterate over assigned tasks and build tasks object
    tasks = []
    for task in assigned_tasks:
        retrieved_task = db.get_task(task)
        tags = ','.join(sorted(retrieved_task['tags'].split(',')))
        retrieved_task['tags'] = tags
        tasks.append(retrieved_task)

    tags = ','.join(db.get_used_tags())
    return render_template('index.html', tasks=tasks, tags=tags)

@app.route('/test_db/')
def test_db():
    return db.test()

@app.route('/create_task_form', methods=['GET'])
def show_task_form():

    return render_template('create_tasks.html')

@app.route('/task', methods=['POST'])
def create_task():
    task = {}
    if request.method == 'POST':
        task['name'] = request.form['task-name']
        task['description'] = request.form['task-description']
        task['status'] = request.form['task-status']
        task['assignee'] = request.form['task-assignee']
        task['priority'] = request.form['task-priority']
        task['severity'] = request.form['task-severity']
        task['created_date'] = str(datetime.now().replace(microsecond=0))
        db.create_task(task, org, username=username)

    return render_template('create_tasks.html')

@app.route('/queue_form', methods=['GET'])
def show_queue_form():

    return render_template('create_queue.html')


@app.route('/queue', methods=['POST'])
def create_queue():
    if request.method == 'POST':
        name  = request.form['queue-name']
    db.create_queue(name, org)

    return render_template('create_queue.html')

@app.route('/task/<task_id>/tags/', methods=['POST'])
def task_tags(task_id):
    db.set_tags(task_id, json.loads(request.form['tags']))
    return Response(status=200)
