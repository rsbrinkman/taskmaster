from taskmaster import app, db
from flask import render_template, request
from datetime import datetime

#TODO: Create login interface.
username='Scott Brinkman'

@app.route('/')
def index():
    # Get set of assigned tasks
    assigned_tasks = db.get_assigned_tasks(username)

    # Iterate over assigned tasks and build tasks object
    tasks  = []
    for task in assigned_tasks:
        tasks.append(db.get_tasks(task).copy())

    return render_template('index.html', tasks=tasks)

@app.route('/test_db/')
def test_db():
    return db.test()

@app.route('/create', methods=['POST', 'GET'])
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
        db.create_task('task>%s' % task['name'], task, username)

    return render_template('create_tasks.html')
