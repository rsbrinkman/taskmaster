from flask import Flask

app = Flask(__name__)
app.config.from_object('taskmaster.settings')

import taskmaster.views
