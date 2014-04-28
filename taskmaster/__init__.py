from flask import Flask

app = Flask(__name__)
app.config.from_object('taskmaster.settings')
app.secret_key = 'really_big_secret'

import taskmaster.views
