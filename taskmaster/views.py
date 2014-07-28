import json
import urllib
from taskmaster import app, settings, events
from taskmaster.db import (
    task_model, org_model, user_model, queue_model, style_rules, tags_model, filter_model,
    permission_model, test_redis_db, PermissionTags, ProjectLevels, FieldConflict, NotFound,
    UpdateNotPermitted, InsufficientPermission)
from flask import render_template, request, Response, g, redirect, url_for, flash
from datetime import datetime
from functools import wraps

@app.before_request
def get_user_info():
    g.token = urllib.unquote(request.cookies.get('token', ''))
    g.user = urllib.unquote(request.cookies.get('user', ''))
    g.org = urllib.unquote(request.cookies.get('org', ''))

def logged_in(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user and g.token and user_model.verify_token(g.user, g.token):
            return f(*args, **kwargs)
        else:
            return redirect(url_for('signup'))

    return decorated_function

def require_permission(tag, not_permitted_redirect=None):
    def require_permission_decorator(f):
        @wraps(f)
        @logged_in
        def decorated_function(*args, **kwargs):
            if g.org and permission_model.permitted(g.user, g.org, tag):
                return f(*args, **kwargs)
            elif not_permitted_redirect:
                return redirect(url_for(not_permitted_redirect))
            else:
                raise InsufficientPermission()

        return decorated_function
    return require_permission_decorator


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
    user_tags = set(tags_model.get_for_user(g.user))

    state = {
        'orgs': orgs,
        'user' : user_model.get(g.user),
        'user_tags': list(user_tags),
    }

    if org_id:
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
        org_tags = set(tags_model.get_for_org(org_id))
        filtermap = {filter_id: filter_model.get(filter_id) for filter_id in filter_model.get_for_org(org_id)}
        org_users = list(org_model.get_users(org_id))
        users = [user_model.get(user_id, include=['name', 'id', 'email']) for user_id in org_users]
        tags = list(org_tags.union(user_tags))

        state.update({
            'tasks': org_tasks,
            'queues': queues,
            'tags': tags,
            'taskmap': taskmap,
            'users': users,
            'preferences': style_rules.get(org_id),
            'filtermap': filtermap,
            'org': org_model.get(org_id)
        })

    return state

@app.route('/test_db/')
def test_db():
    return test_redis_db()

#
# HTML Pages
#

@app.route('/')
@require_permission(PermissionTags.VIEW,  not_permitted_redirect='admin')
def index():
    return render_template('index.html', state=json.dumps(_task_state(g.org)))

@app.route('/admin')
@logged_in
def admin():
    return render_template('admin.html', state=json.dumps(_task_state(g.org)))

@app.route('/project-admin')
@require_permission(PermissionTags.VIEW)
def project_admin():
    return render_template('project_admin.html', state=json.dumps(_task_state(g.org)))

@app.route('/signup')
def signup():
    user = request.args.get('email', '')
    return render_template('sign_up.html', user=user)

#
# USER
#

@app.route('/user/', methods=['POST'])
def create_user():
    user = user_model.create({
        'email': request.form['email'],
        'name': request.form['name'],
        'password': request.form['password'],
    })

    for example_org_name in settings.EXAMPLE_ORGS:
        org_id = org_model.id_from('name', example_org_name)
        if org_id:
            org_model.add_user(org_id, user['id'])

    # Add user to waiting list orgs
    waiting_list = user_model.get_waiting_list(user['email'])
    if waiting_list:
        for org_id in waiting_list:
            org_model.add_user(org_id, user['id'])
    else:
        events.mediator('signed_up', email=user['email'], name=user['name'])

    return Response(json.dumps(user), status=201, content_type='application/json')

@app.route('/user/<_id>/<field>', methods=['PUT'])
@logged_in
def update_user(_id, field):
    if g.user != _id:
        raise UpdateNotPermitted(field)

    user_model.update(_id, field, request.form['value'])
    return Response(status=200)

@app.route('/user/<_id>', methods=['DELETE'])
@require_permission(PermissionTags.EDIT_TASK)
def delete_user(_id):
    if g.user != _id:
        raise InsufficientPermission()

    user_model.delete(_id)
    return Response(status=204)

@app.route('/authenticate', methods=['POST'])
def authenticate():
    try:
        user = user_model.login(request.form['email'], request.form['password'])
    except NotFound:
        user = None

    if user:
        return Response(json.dumps(user), status=200, content_type='application/json')
    else:
        return Response('Email address and password do not match any user', status=401)

@app.route('/logout', methods=['POST'])
@logged_in
def logout():
    user_model.logout(g.user)
    return Response(status=200)

#
# ORG
#

@app.route('/org/', methods=['POST'])
@logged_in
def create_org():
    org = org_model.create({
        'owner': g.user,
        'name': request.form['name'],
    })
    return Response(json.dumps(org), status=201, content_type='application/json')

@app.route('/org/<_id>/<field>', methods=['PUT'])
@require_permission(PermissionTags.EDIT_ORG)
def update_org(_id, field):
    org_model.update(_id, field, request.form['value'])
    return Response(status=200)

@app.route('/org/<orgname>/user/<username>/', methods=['POST'])
@logged_in
def add_user_to_org(orgname, username):
    org_id = org_model.id_from('name', orgname)
    role = 'editor'

    if not (permission_model.permitted(g.user, org_id, PermissionTags.EDIT_USER) and
            permission_model.role_gte(g.user, org_id, role)):
        raise InsufficientPermission()

    user_id = user_model.id_from('email', username)
    if user_id:
        org_model.add_user(org_id, user_id)
        events.mediator('added_to_project', email=username, project=org_id)
    else:
        # Add user to waiting list
        user_model.add_to_waiting_list(username, org_id)
        events.mediator('invite', email=username, org_id=org_id)

    org = org_model.get(org_id)
    return Response(json.dumps(org), status=200, content_type='application/json')

@app.route('/search/orgs/', methods=['POST'])
@logged_in
def search_org():
    org_id = org_model.id_from('name', request.args.get('term'))
    org = org_model.get(org_id)

    if not permission_model.permitted(g.user, org_id, PermissionTags.VIEW):
        org = {}

    return Response(json.dumps(org), content_type='application/json')

#
# TASK
#

@app.route('/task/', methods=['POST'])
@require_permission(PermissionTags.EDIT_TASK)
def create_task():
    task = task_model.create({
        'name': request.form['task-name'],
        'org': g.org,
        'description': request.form['task-description'],
        'status': request.form['task-status'],
        'assignee': request.form['task-assignee'],
        'created_date': str(datetime.now().date()),
        'queue': request.form['task-queue'],
    })
    return Response(json.dumps(task), status=201, content_type='application/json')

@app.route('/task/<_id>/<field>', methods=['PUT'])
@require_permission(PermissionTags.EDIT_TASK)
def update_task(_id, field):
    if field == 'tags':
        tags_model.set(_id, g.user, json.loads(request.form['value']))
    else:
        task_model.update(_id, field, request.form['value'])

    if field == 'assignee':
        events.mediator('assigned', task_id=_id, user_id=request.form['value'])
    if field == 'status':
        events.mediator('status_update', task_id=_id)

    return Response(status=200)

@app.route('/order/task', methods=['PUT'])
@app.route('/order/task/<queue_id>', methods=['PUT'])
@require_permission(PermissionTags.EDIT_TASK)
def update_task_order(queue_id=None):
    task_model.update_order(g.org, json.loads(request.form['updates']), queue_id=queue_id)
    return Response(status=200)

@app.route('/task/<_id>', methods=['DELETE'])
@require_permission(PermissionTags.EDIT_TASK)
def delete_task(_id):
    task_model.delete(_id)
    return Response(status=204)

#
# QUEUE
#

@app.route('/queue/', methods=['POST'])
@require_permission(PermissionTags.EDIT_QUEUE)
def create_queue():
    queue = queue_model.create({
        'name': request.form['name'],
        'org': g.org,
    })
    return Response(json.dumps(queue), status=201, content_type='application/json')

@app.route('/queue/<_id>/<field>', methods=['PUT'])
@require_permission(PermissionTags.EDIT_QUEUE)
def update_queue(_id, field):
    queue_model.update(_id, field, request.form['value'])
    return Response(status=200)

@app.route('/order/queue', methods=['PUT'])
@require_permission(PermissionTags.EDIT_QUEUE)
def update_queue_order():
    queue_model.update_order(g.org, json.loads(request.form['updates']))
    return Response(status=200)

@app.route('/queue/<_id>', methods=['DELETE'])
@require_permission(PermissionTags.EDIT_QUEUE)
def delete_queue(_id):
    queue_model.delete(_id)
    return Response(status=204)

#
# FILTER
#

@app.route('/filter/', methods=['POST'])
@require_permission(PermissionTags.EDIT_FILTER)
def create_filter():
    obj = filter_model.create({
        'name': request.form['name'],
        'rule': request.form['rule'],
        'org': g.org,
    })

    return Response(json.dumps(obj), status=201, content_type='application/json')

@app.route('/filter/<_id>', methods=['DELETE'])
@require_permission(PermissionTags.EDIT_FILTER)
def delete_filter(_id):
    filter_model.delete(_id)
    return Response(status=204)

#
# ERROR HANDLERS
#

@app.errorhandler(FieldConflict)
def handle_field_conflict(e):
    return Response(e.message, status=409)

@app.errorhandler(UpdateNotPermitted)
def handle_update_not_permitted(e):
    return Response(e.message, status=403)

@app.errorhandler(NotFound)
def handle_not_found(e):
    return Response(e.message, status=404)

@app.errorhandler(InsufficientPermission)
def handle_insufficent_permission(e):
    return Response(e.message, status=403)
