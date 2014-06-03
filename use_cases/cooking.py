TASKS = {
    "pickles": {
        "name": "Spicy Pickles!",
        "description": """1:1 Water to white vinegar
1 tablespoon pickling spice
1 tablespoon sugar
2 tablespoons salt
LOTS of crushed red pepper
Submerged cucumbers, jalepenos, carrots, beans etc in liquid and stuff into jars
Refrigerate"""
    },

    "burger": {
        "name": "Stuffed Jalapeno Burger",
         "description": """- Stuff a jalepeno with cheese
- Wrap in ground chuck mixed with onions and spices
- Grill like a boss
- Ruin burgers for everyone ever again"""
    },

    "salmon": {
        "name": "Panko Encrusted Salmon",
        "description": """1 salmon filet skin on
Slather on mustard
Make panko crust
- 1 cup pank
- chopped parsley
- grated parmesan
- crushed garlic
Press panko crust into salmon
Cook skin down in cast iron skillet for 5 minutes
Move to broiler for to finish"""
    },

    "trout": {
        "name": "prosciutto wrapped trout",
        "description": """Remove skin
Wrap in prosciutto
Pan fry"""
    },
}

PROJECTS = [
    {
        "name": "Things to Cook",
        "queues": [
            {
                "name": "Grilling Ideas",
                "tasks": ["burger"],
            },
            {
                "name": "Fish",
                "tasks": ["salmon", "trout"],
            },
            {
                "name": "Pickles",
                "tasks": ["pickles"],
            },
        ],
        "tags": {
            "burger": ["entrees"],
            "trout": ["entrees"],
            "salmon": ["entrees"],
        },

        "tasks": TASKS
    },
    {
        "name": "Things to Cook 2",
        "queues": [
            {
                "name": "Entrees",
                "tasks": ["burger", "salmon", "trout"],
            },
            {
                "name": "Desserts",
                "tasks": [],
            },
            {
                "name": "Experiments",
                "tasks": ["pickles"],
            },
        ],
        "tags": {
            "burger": ["beef", "spicy"],
            "trout": ["fish"],
            "salmon": ["fish"],
            "pickles": ["spicy", "vegetarian"],
        },

        "tasks": TASKS
    },
]
