from flask_wtf import Form
from wtforms import SubmitField, SelectField


class FindNpc(Form):
    level_choice = SelectField('Level')
    race_choice = SelectField('Race')
    archetype_choice = SelectField('Archetype')
    submit = SubmitField('Ask the barkeep')
