TASKS = {
    "mocks": {
        "name": "Create Initial Mocks for New Product Idea",
        "description": """Mocks should include:
- Lightweight UI and user interactions
- Basic workflows
- Fleshed out value propisition"""
    },
    "views": {
        "name": "Build base views",
        "description": """Build initial app views using backbone.js
- View should serve an index.html
- Include all required libraries - jquery, underscore, bootstrap
- Hell world text"""
    },
    "server": {
        "name": "Build out basic web server",
        "description": """Write a base web server to serve initial views and interact with the db
- Should have route to render index.html
- Should have conn to db (redis)"""
    },
    "hello": {
        "name": "Deploy hello world app to domain",
        "description": """Deploy mocked view and web server to test.jpmunz.com and let everyone know its up
- Create a script to automatically update the deployed app from git"""
    },
    "simple": {
        "name": "Make an amazing and simple task management app",
        "description": """Focus on helping teams to interact more efficiently
- Create tasks, bucket them for collaboration, and manage your projects in a social way"""
    },
}

PROJECTS = [
    {
        "name": "New Product",
        "queues": [
            {
                "name": "Design",
                "tasks": ["mocks"],
            },
            {
                "name": "Front End",
                "tasks": ["views"],
            },
            {
                "name": "Backend",
                "tasks": ["server", "hello"],
            },
            {
                "name": "Crazy Ideas",
                "tasks": ["simple"],
            },
        ],
        "tags": {
        },
        "tasks": TASKS
    }
]
