from taskmaster import app, db
from flask import render_template, request
from datetime import datetime

@app.route('/')
def index():
    tasks  = {}
    tasks = db.get_tasks('example_task')

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
        task['created_date'] = str(datetime.now().replace(microsecond=0))
        db.create_task(task['name'], task)

    return render_template('create_tasks.html')
