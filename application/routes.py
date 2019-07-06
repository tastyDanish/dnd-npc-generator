from flask import render_template, request
from application import application
from application.npc import NPC
from application.forms import FindNpc
from application.models import Attributes


@application.route('/', methods=['GET', 'POST'])
@application.route('/index', methods=['GET', 'POST'])
def index(find_level=1, find_race=None, find_archetype=None):
    form = FindNpc()

    form.level_choice.choices = [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'),
                                 ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'), ('10', '10'),
                                 ('11', '11'), ('12', '12'), ('13', '13'), ('14', '14'), ('15', '15'),
                                 ('16', '16'), ('17', '17'), ('18', '18'), ('19', '19'), ('20', '20')]

    race_attrs = Attributes.query.filter_by(attribute='Race').all()
    form.race_choice.choices = [('None', 'Person')] + [(x.value, x.value) for x in race_attrs]

    archetype_attrs = Attributes.query.filter_by(attribute='Archetype')
    form.archetype_choice.choices = [('None', 'Anything')] + [(x.value, x.value) for x in archetype_attrs]

    if request.method == 'GET':
        form.level_choice.data = find_level
        form.race_choice.data = find_race
        form.archetype_choice.data = find_archetype
    elif request.method == 'POST':
        if form.validate_on_submit():
            find_level = form.level_choice.data
            find_race = form.race_choice.data
            find_archetype = form.archetype_choice.data

    my_npc = NPC()
    print('level {} race {} archetype {}'.format(find_level, find_race, find_archetype))
    my_npc.generate_npc(level=find_level, race=find_race, archetype=find_archetype)
    return render_template('index.html', npc=my_npc, form=form)
