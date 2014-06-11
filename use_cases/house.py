TASKS = {
    "pots": {
        "name": "Buy Pots & Pans",
        "description": """We need:
- Large Saucepan (14")
- Small frying pan (5")
    - Medium frying pan (10")
- Large frying pan (14")""",
        "status": "Done"
    },
    "dishes": {
        "name": "Dish washing paraphanelia",
        "description": """We need:
- Dish Rags
- Dish Soap
- Sponges
- Dish Scrubber
- Drying Rack"""
    },
    "kitchen": {
        "name": "Kitchen Decoration Crap",
        "description": """Our walls are bare and they need more crap. Let's find some crap for the walls."""
    },
    "cook": {
        "name": "Cook at least 3 times a week",
        "description": """We're saving money since we just bought this big ass house and we should eat in more.
- Must be something cheap and healthy
- We'll reassign every week back and forth
- The person is 'off' this week gets to do dishes :)"""
    },
    "couch": {
        "name": "Buy a couch",
        "description": """see above"""
    },
    "tv": {
        "name": "Buy a TV",
        "description": """That thing better be a monster and we need to put it on the wall to save space for activities"""
    },
    "clean": {
        "name": "Clean the living room once a week",
        "description": """A recurring task to trade off back and forth. Cleaning the living room means:
- Vacuum
- Swiffer
- Dust
No excuses. Play like a champion"""
    },
}

PROJECTS = [
    {
        "name": "New House",
        "queues": [
            {
                "name": "Kitchen",
                "tasks": ["pots", "dishes", "kitchen", "cook"],
            },
            {
                "name": "Living Room",
                "tasks": ["couch", "tv", "clean"],
            },
            {
                "name": "Bedroom",
                "tasks": [],
            },
            {
                "name": "Backyard",
                "tasks": [],
            },
            {
                "name": "Weekly Chores",
                "tasks": [],
            },
        ],
        "tags": {
            "pots": ["Stuff to Buy"],
            "dishes": ["Stuff to Buy"],
            "kitchen": ["Stuff to Buy"],
            "couch": ["Stuff to Buy"],
            "tv": ["Stuff to Buy"],
            "cook": ["Recurring Chores"],
            "clean": ["Recurring Chores"],
        },
        "tasks": TASKS
    },

    {
        "name": "New House 2",
        "queues": [
            {
                "name": "To Buy",
                "tasks": ["pots", "dishes", "kitchen", "couch", "tv"],
            },
            {
                "name": "Weekly Chores",
                "tasks": ["cook", "clean"],
            },
        ],
        "tags": {
            "pots": ["kitchen"],
            "dishes": ["kitchen"],
            "kitchen": ["kitchen"],
            "couch": ["living room"],
            "tv": ["living room"],
            "clean": ["living room"],
        },
        "tasks": TASKS
    },
]
