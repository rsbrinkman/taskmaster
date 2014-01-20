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
        if retrieved_task:
            tags = ','.join(sorted(retrieved_task['tags'].split(',')))
            retrieved_task['tags'] = tags
            tasks.append(retrieved_task)
        else:
            db.remove_assigned_task(username, task)

    tags = ','.join(db.get_used_tags())
    queues = db.get_org_queues(org)
    return render_template('index.html', tasks=tasks, tags=tags, queues=queues)

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


@app.route('/queue/<name>', methods=['POST'])
def create_queue(name):
    db.create_queue(name, org)

    return render_template('create_queue.html')

@app.route('/task/<task_id>', methods=['DELETE'])
def task_update(task_id):
    if request.method == 'DELETE':
        db.delete_task(task_id, org)
        return Response(status=200)

@app.route('/task/<task_id>/tags/', methods=['POST'])
def task_tags(task_id):
    db.set_tags(task_id, json.loads(request.form['tags']))

    return Response(status=200)

@app.route('/queue/<queue_name>', methods=['DELETE'])
def update_queue(queue_name):
    if request.method == 'DELETE':
        db.delete_queue(queue_name, org)

        return Response(status=200)

@app.route('/queue/<queue_name>/<task_id>', methods=['POST'])
def add_task_to_queue(queue_name, task_id):
    if request.method == 'POST':
        db.add_task_to_queue(task_id, queue_name)

        return Response(status=200)

@app.route('/task/<task_id>/update/<update_field>/<update_value>', methods=['POST'])
def update_task(task_id, update_field, update_value):
    db.update_task(task_id, update_field, update_value)

    return Response(status=200)
