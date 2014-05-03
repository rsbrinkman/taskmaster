from flask import Flask

app = Flask(__name__)
app.config.from_object('taskmaster.settings')
app.secret_key = 'p\x81\xbd\xfb.q\xa3\xf4\xd3\xab\x03u\xbe\x0e\xdb\xc7$9\xaey3Fr\x1c'

import taskmaster.views
