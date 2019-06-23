from flask import render_template, request
from application import application, db
from application.npc import NPC


@application.route('/')
@application.route('/index')
def index():
    my_npc = NPC()
    return render_template('index.html', npc=my_npc)
