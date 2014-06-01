TASKS = {
    "jennifer": {
        "name": "Send Jennifer proposal",
        "description": """100k MAU
Budget is 5k/month
Wants 50% discount from list
Major use cases: Faster task management, better teamwork. No more jira"""
    },
    "newco": {
        "name": "Contact NewCo in June",
        "description": """No engineering resources available until June, reach out to john@newco.com
salesforce.com/link_to_opportunity"""
    },
    "bear": {
        "name": "Hungry Bear",
        "description": """hungrybear.com - could be a good use case for us
hungry@bear.com to reach out
mobile developer of teddy bear apps."""
    },
    "flowers": {
        "name": "1 800 flowers - throw up a hail mary",
        "description": """Had multiple conversations and have sent over terms, but was deprioritized indefinitely
- Ping lauren@flowers.com to check in and keep warm
- Proceed at own risk, Scott has given up on this one
salesforce.com/link_to_worst_opp_ever"""
    },
}

PROJECTS = [
    {
        "name": "Sales",
        "queues": [
            {
                "name": "Hit List",
                "tasks": ["jennifer"],
            },
            {
                "name": "Follow Ups",
                "tasks": ["newco"],
            },
            {
                "name": "New Leads",
                "tasks": ["bear"],
            },
            {
                "name": "Long Shots",
                "tasks": ["flowers"],
            },
        ],
        "tags": {
            "taskid": [],
        },
        "tasks": TASKS
    }
]
