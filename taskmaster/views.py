import json
import urllib
from taskmaster import app, db, settings
from taskmaster.db import task_model, org_model, user_model, queue_model, style_rules, test_redis_db, FieldConflict, NotFound
from flask import render_template, request, Response, g, redirect, url_for, flash
from datetime import datetime
from functools import wraps

default_user = 'Joe'

def require_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user and g.token and user_model.verify_token(g.user, g.token):
            return f(*args, **kwargs)
        else:
            flash('Please login and select a project')
            return redirect(url_for('signup'))

    return decorated_function

def require_org(f):
    @wraps(f)
    @require_user
    def decorated_function(*args, **kwargs):
        if g.org and org_model.has_user(g.org, g.user):
            return f(*args, **kwargs)
        else:
            flash('Please select a project')
            return redirect(url_for('admin'))

    return decorated_function

def _task_state(org_id=None):
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
    orgs = list(org_model.get_for_user(g.user))

    # Get set of assigned tasks
    org_tasks = list(task_model.get_for_org(org_id))

    # Iterate over assigned tasks and build tasks object
    taskmap = {}
    for task in org_tasks:
        retrieved_task = task_model.get(task)
        if retrieved_task:
            tags = ','.join(sorted(retrieved_task['tags'].split(',')))
            retrieved_task['tags'] = tags
            taskmap[retrieved_task['id']] = retrieved_task
        else:
            task_model.remove_from_org(org_id, task)

    queues = queue_model.get_for_org(org_id)

    tags = list(db.get_used_tags())

    filters = db.get_saved_filters(g.user)

    org_users = list(org_model.get_users(org_id))
    users = [user_model.get(user_id, include=['name', 'id']) for user_id in org_users]

    return {
        'tasks': org_tasks,
        'queues': queues,
        'tags': tags,
        'taskmap': taskmap,
        'users': users,
        'preferences': style_rules.get(org_id),
        'filtermap': filters,
        'user' : g.user,
        'orgs': orgs,
        'org': org_model.get(org_id)
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
    return test_redis_db()

@app.route('/admin')
@require_user
def admin():
    user = user_model.get(g.user)
    return render_template('admin.html', user=user)

@app.route('/signup')
def signup():
    return render_template('sign_up.html')

@app.route('/user', methods=['POST'])
def create_user():
    user_dict = {
        'email': request.form['email'],
        'name': request.form['name'],
        'password': request.form['password'],
    }

    try:
        user = user_model.create(user_dict)
        for example_org_name in settings.EXAMPLE_ORGS:
            org_id = org_model.id_from_name(example_org_name)
            if org_id:
                org_model.add_user(org_id, user['id'])

        return Response(json.dumps(user), status=201, content_type='application/json')
    except FieldConflict, e:
        return Response(e.message, status=409)

@app.route('/authenticate', methods=['POST'])
def authenticate():
    try:
        user = user_model.login(request.form['email'], request.form['password'])
    except NotFound:
        user = None

    if user:
        return Response(json.dumps(user), status=200, content_type='application/json')
    else:
        return Response('Email address and password do not match any user', status=400)

@app.route('/logout', methods=['POST'])
@require_user
def logout():
    user_model.logout(g.user)
    return Response(status=200)

@app.route('/user/<user_id>/<update_field>/<update_value>', methods=['POST'])
def update_user(user_id, update_field, update_value):
    user_model.update(user_id, update_field, update_value)
    return Response(status=200)

@app.route('/org/<orgname>', methods=['POST'])
def create_org(orgname):
    org = {
        'owner': g.user,
        'name': orgname,
    }

    org = org_model.create(org)

    return Response(json.dumps(org), status=201, content_type='application/json')

@app.route('/org/<orgname>/user/<username>', methods=['POST'])
def add_user_to_org(orgname, username):
    if request.method == 'POST':
        org_id = org_model.id_from_name(orgname)
        user_id = user_model.id_from_email(username)

        org_model.add_user(org_id, user_id)
        org = org_model.get(org_id)

    return Response(json.dumps(org), status=200, content_type='application/json')

@app.route('/orgs/<orgname>', methods=['POST'])
def search_org(orgname):
    if request.method == 'POST':
        org_id = org_model.id_from_name(orgname)
        org = org_model.get(org_id)

    return Response(json.dumps(org), content_type='application/json')

@app.route('/task', methods=['POST'])
def create_task():
    task = {
        'name': request.form['task-name'],
        'org': g.org,
        'description': request.form['task-description'],
        'status': request.form['task-status'],
        'assignee': request.form['task-assignee'],
        'created_date': str(datetime.now().date()),
        'queue': request.form['task-queue'],
    }

    task = task_model.create(task)

    return Response(json.dumps(task), status=201, content_type='application/json')

@app.route('/queue_form', methods=['GET'])
def show_queue_form():
    return render_template('create_queue.html')


@app.route('/queue/<name>', methods=['POST'])
def create_queue(name):
    queue_obj = {
        'name': name,
        'org': g.org,
    }

    queue = queue_model.create(queue_obj)
    return Response(json.dumps(queue), status=201, content_type='application/json')

@app.route('/task/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    if request.method == 'DELETE':
        task_model.delete(task_id)
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
    queue_model.update_order(g.org, json.loads(request.form['updates']))
    return Response(status=200)

@app.route('/order/task/', methods=['PUT'])
@app.route('/order/task/<queue_name>', methods=['PUT'])
def update_task_order(queue_name=''):
    task_model.update_order(g.org, json.loads(request.form['updates']), queue_name=queue_name)
    return Response(status=200)

@app.route('/queue/<queue_id>', methods=['DELETE'])
def delete_queue(queue_id):
    if request.method == 'DELETE':
        queue_model.delete(queue_id)
        return Response(status=200)

@app.route('/queue/<queue_id>/update/<update_field>/<update_value>', methods=['POST'])
def update_queue(queue_id, update_field, update_value):
    queue_model.update(queue_id, update_field, update_value)
    return Response(status=200)

@app.route('/task/<task_id>/update/<update_field>/', methods=['POST'])
@app.route('/task/<task_id>/update/<update_field>/<update_value>', methods=['POST'])
def update_task(task_id, update_field, update_value=''):
    task_model.update(task_id, update_field, update_value)
    return Response(status=200)
