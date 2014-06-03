TASKS = {
    "taskid": {
        "name": "",
        "description": """
        """
    },
}

PROJECTS = [
    {
        "name": "project",
        "queues": [
            {
                "name": "queue",
                "tasks": ["taskid"],
            },
        ],
        "tags": {
            "taskid": [],
        },
        "tasks": TASKS
    }
]
