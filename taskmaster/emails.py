WELCOME = """
    <p>Welcome to Taskmaster! We're excited to have you here %(name)s.</p>

    <p>To get started:
    <ol>
        <li>Choose an <a href="%(base_url)s" target="_blank">example project</a> to take a tour</li>
        <li>Create your <a href="%(base_url)s/admin" target="_blank">own projects</a></li>
        <li>Get stuff done more efficiently!</li>
    </ol>
    </p>

    <p>Thanks, <br>
    Scott & Jon</p>
"""

ADDED_TO_PROJECT = """
    <p>You've been added to a project! Check it out <a href="%(base_url)s" target="_blank">here</a> to get started</p>

    <p>Thanks, <br>
    Taskmaster</p>
"""

ASSIGNED_TASK = """
    <p>You've been assigned %(task)s. Time to get to <a href="%(base_url)s" target="_blank">work</a>!</p>
    <p>Thanks, <br>
    Taskmaster</p>
"""

TASK_STATUS_CHANGE = """
    <p>Your task %(task)s's status has been updated to %(status)s</p>
    <p>Thanks, <br>
    Taskmaster</p>
"""
INVITED = """
    <p>Hi,</p>

    <p>You've been added to <strong>%(project)s</strong>, a <a href="%(base_url)s" target="_blank">Taskmaster</a> project, but haven't signed up yet.</p>
    <p>Taskmaster is social project management and someone wants you to join!</p>
    <p>To get started:<br>
    <ul>
        <li><a href="%(base_url)s/signup" target="_blank">Sign Up</li>
        <li>Check out %(project)s, the project you were added to!</li>
        <li>Explore other example projects</li>
        <li>Create your own projects</li>
    </ul>
    </p>
"""
