from taskmaster import app, db
from flask import render_template

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test_db/')
def test_db():
    return db.test()
