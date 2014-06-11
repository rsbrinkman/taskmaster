TASKS = {
    "problem": {
        "name": "Problem Set #1",
        "description": """- Due on 6/1
http://link_to_problem_set.biz/homework"""
    },
    "psychmidterm": {
        "name": "Mid Term Paper Psych 101",
        "description": """Requirements:
10 - 15 pages
At least 10 sources cited
Topic of my choice"""
    },
    "psychfinal": {
        "name": "Psychology of Music Final",
        "description": """Study Guide can be found here: www.studyguide.com/bizness
- 12 short answer questions
- All topic covered in reading over semester
- Average grade was C+ last semester :("""
    },
    "stats": {
        "name": "Statistics Reading",
        "description": """Pages 113-200
Due on 6/15"""
    },
}

PROJECTS = [
    {
        "name": "Homework",
        "queues": [
            {
                "name": "Finals",
                "tasks": ["psychfinal"],
            },
            {
                "name": "Mid Terms",
                "tasks": ["psychmidterm"],
            },
            {
                "name": "Weekly Work",
                "tasks": ["problem", "stats"],
            },
        ],
        "tags": {
            "psychfinal": ["psych101"],
            "psychmidterm": ["psych101"],
            "problem": ["stats220"],
            "stats": ["stats220"],
        },
        "tasks": TASKS
    },
    {
        "name": "Homework 2",
        "queues": [
            {
                "name": "Psych 101",
                "tasks": ["psychmidterm", "psychfinal"],
            },
            {
                "name": "Stats 220",
                "tasks": ["stats", "problem"],
            },
        ],
        "tags": {
            "psychfinal": ["final"],
            "psychmidterm": ["midterm"],
            "problem": ["weekly"],
            "stats": ["weekly"],
        },
        "tasks": TASKS
    }
]
