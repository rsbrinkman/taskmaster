import json

from taskmaster import app, db
from flask import render_template, request, Response
from datetime import datetime

#TODO: Create login interface.
org = 'Taskmaster'
users = [
    'Scott Brinkman',
    'Jon Munz',
]

def _task_state():
    '''
    Returns a JSON representation of the user's current tasks and queues, used to
    render the client-side DOM.

    For objects a seperate list of their ids is maintained (e.g. tasks and taskmap), this
    is so we can preserve the order of the objects and still be able to access properties
    directly if we know the id.

    {
        'tasks': [ 't1', 't2', ... ],
        'queues': [ 'q1', 'q2', .... ],
        'taskmap': {
            'id1': {},
            'id2': {}
        },
        'queuemap': {
            'id1': {},
            'id2': {}
        },
        'tags': [ 'tag1', 'tag2', ... ]
    }
    '''
    # Get set of assigned tasks
    org_tasks = list(db.get_org_tasks(org))
    #TODO sort the list of tasks

    # Iterate over assigned tasks and build tasks object
    taskmap = {}
    for task in org_tasks:
        retrieved_task = db.get_task(task)
        if retrieved_task:
            tags = ','.join(sorted(retrieved_task['tags'].split(',')))
            retrieved_task['tags'] = tags
            taskmap[retrieved_task['id']] = retrieved_task
        else:
            db.remove_org_task(org, task)

    # (queuename, queuetasks)
    queue_tasks = db.get_org_queues(org)
    queuemap = {}
    for queue in queue_tasks:
        queuemap[queue[0]] = {
            'id': queue[0],
            'tasks': queue[1],
            'selected': False, #TODO, remember what the user had last
        }
    queues = [queue[0] for queue in queue_tasks]
    # TODO sort the list of queues

    tags = list(db.get_used_tags())

    return {
        'tasks': org_tasks,
        'queues': queues,
        'tags': tags,
        'taskmap': taskmap,
        'queuemap': queuemap,
        'users': users,
    }

@app.route('/')
def index():
    return render_template('index.html', state=json.dumps(_task_state()))

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
        task['queue'] = ''
        db.create_task(task, org)

    return render_template('create_tasks.html')

@app.route('/queue_form', methods=['GET'])
def show_queue_form():
    return render_template('create_queue.html')


@app.route('/queue/<name>', methods=['POST'])
def create_queue(name):
    db.create_queue(name, org)

    #TODO unified way to get json from queue, duplicated in _get_state
    queue_obj = {
        'id': name,
        'tasks': [],
        'selected': False,
    }

    return Response(json.dumps(queue_obj), content_type='application/json')

@app.route('/task/<task_id>', methods=['DELETE'])
def task_update(task_id):
    if request.method == 'DELETE':
        db.delete_task(task_id, org)
        return Response(status=200)

@app.route('/task/<task_id>/tags/', methods=['POST'])
def task_tags(task_id):
    db.set_tags(task_id, json.loads(request.form['tags']))

    return Response(status=200)

@app.route('/order/queue/', methods=['PUT'])
def update_queue_order():
    db.update_queue_order(org, json.loads(request.form['updates']))
    return Response(status=200)

@app.route('/queue/<queue_name>', methods=['DELETE'])
def update_queue(queue_name):
    if request.method == 'DELETE':
        db.delete_queue(queue_name, org)
        return Response(status=200)

@app.route('/task/<task_id>/update/<update_field>/', methods=['POST'])
@app.route('/task/<task_id>/update/<update_field>/<update_value>', methods=['POST'])
def update_task(task_id, update_field, update_value=''):
    db.update_task(task_id, update_field, update_value)

    return Response(status=200)
