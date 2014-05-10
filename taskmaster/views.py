import json
import ast
import urllib
from taskmaster import app, db, settings
from flask import render_template, request, Response, g, redirect, url_for, flash
from datetime import datetime
from functools import wraps

#TODO: Create login interface.
#org = 'Taskmaster'
default_user = 'Joe'

users = [
    'Scott Brinkman',
    'Jon Munz',
]

def require_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user and g.token and db.verify_token(g.user, g.token):
            return f(*args, **kwargs)
        else:
            flash('Please login and select an org')
            return redirect(url_for('signup'))

    return decorated_function

def require_org(f):
    @wraps(f)
    @require_user
    def decorated_function(*args, **kwargs):
        if g.org and g.org in db.get_user_orgs(g.user):
            return f(*args, **kwargs)
        else:
            flash('Please select an org')
            return redirect(url_for('admin'))

    return decorated_function

def _task_state(org=None):
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
    # Get the user's orgs
    orgs = list(db.get_user_orgs(g.user))

    # Get a chosen or default org
    if not org:
        # this is dumb, but easy until we build a 'primary' org concept
        org = orgs[0]
    # Get set of assigned tasks
    org_tasks = list(db.get_org_tasks(org))

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
            'tasks': queue[1]
        }
    queues = [queue[0] for queue in queue_tasks]

    tags = list(db.get_used_tags())

    preferences = db.get_user_preferences(default_user)

    filters = db.get_saved_filters(g.user)

    users = list(db.get_org_users(org))

    return {
        'tasks': org_tasks,
        'queues': queues,
        'tags': tags,
        'taskmap': taskmap,
        'queuemap': queuemap,
        'users': users,
        'preferences': preferences,
        'filtermap': filters,
        'user' : g.user,
        'orgs': orgs,
        'org': org
    }

@app.before_request
def get_user_info():
    g.token = urllib.unquote(request.cookies.get('token', ''))
    g.user = urllib.unquote(request.cookies.get('user', ''))
    g.org = urllib.unquote(request.cookies.get('org', ''))

@app.route('/', methods=['GET'])
@require_org
def index():
    return render_template('index.html', state=json.dumps(_task_state(g.org)))

@app.route('/test_db/')
def test_db():
    return db.test()

@app.route('/admin')
@require_user
def admin():
    user = db.get_user(g.user)
    return render_template('admin.html', user=user)

@app.route('/signup')
def signup():
    return render_template('sign_up.html')

@app.route('/user', methods=['POST'])
def create_user():
    email = request.form['email']
    name = request.form['name']
    password = request.form['password']

    try:
        token = db.create_user(email, name, password)

        for example_org in settings.EXAMPLE_ORGS:
            db.add_user_to_org(example_org, email)

        return Response(token, status=201)
    except db.UserConflict:
        return Response("Email address already in use", status=409)

@app.route('/authenticate', methods=['POST'])
def authenticate():
    token = db.login_user(request.form['email'], request.form['password'])

    if token:
        return Response(token, status=200)
    else:
        return Response('Email address and password do not match any user', status=400)

@app.route('/logout', methods=['POST'])
@require_user
def logout():
    db.logout_user(g.user)
    return Response(status=200)

@app.route('/org/<orgname>', methods=['POST'])
def create_org(orgname):
    if request.method == 'POST':
        users = request.form['users']
        db.create_org(orgname, admin=users)

    return Response(status=200)

@app.route('/org/<orgname>/user/<username>', methods=['POST'])
def add_user_to_org(orgname, username):
    if request.method == 'POST':
        db.add_user_to_org(orgname, username)

    return Response(status=200)

@app.route('/orgs/<orgname>', methods=['POST'])
def search_org(orgname):
    if request.method == 'POST':
        org = db.get_org(orgname)
    return Response(json.dumps(org), content_type='application/json')



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
        task['created_date'] = str(datetime.now().date())
        if request.form['task-queue'] == 'no-queue':
            #TODO: Use this to set a the 'null' queue in UI/UX queue
            #TODO: This is a good opportunity to link to a task.
            task['queue'] = ''
        task['queue'] = request.form['task-queue']
        # Grab the org from the cookie
        task = db.create_task(task, g.org)

    return Response(json.dumps(task), content_type='application/json')

@app.route('/queue_form', methods=['GET'])
def show_queue_form():
    return render_template('create_queue.html')


@app.route('/queue/<name>', methods=['POST'])
def create_queue(name):
    db.create_queue(name, g.org)

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
        db.delete_task(task_id, g.org)
        return Response(status=200)

@app.route('/task/<task_id>/tags/', methods=['POST'])
def task_tags(task_id):
    db.set_tags(task_id, json.loads(request.form['tags']))

    return Response(status=200)

@app.route('/filter/<filtername>/', methods=['POST', 'DELETE'])
def manage_user_filter(filtername):
    if request.method == 'POST':
        rule = request.form['rule']
        obj = db.create_filter(g.user, filtername, rule)
        return Response(json.dumps(obj), content_type='application/json')
    elif request.method == 'DELETE':
        db.delete_filter(g.user, filtername)
        return Response(status=200)

@app.route('/order/queue/', methods=['PUT'])
def update_queue_order():
    db.update_queue_order(g.org, json.loads(request.form['updates']))
    return Response(status=200)

@app.route('/order/task/', methods=['PUT'])
@app.route('/order/task/<queue_name>', methods=['PUT'])
def update_task_order(queue_name=''):
    db.update_task_order(g.org, json.loads(request.form['updates']), queue_name=queue_name)
    return Response(status=200)

@app.route('/queue/<queue_name>', methods=['DELETE'])
def update_queue(queue_name):
    if request.method == 'DELETE':
        db.delete_queue(queue_name, g.org)
        return Response(status=200)

@app.route('/task/<task_id>/update/<update_field>/', methods=['POST'])
@app.route('/task/<task_id>/update/<update_field>/<update_value>', methods=['POST'])
def update_task(task_id, update_field, update_value=''):
    db.update_task(task_id, update_field, update_value)

    return Response(status=200)
