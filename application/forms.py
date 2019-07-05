from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField


class FindNpc(FlaskForm):
    level_choice = SelectField('Level')
    race_choice = SelectField('Race')
    archetype_choice = SelectField('Archetype')
    submit = SubmitField('Ask the barkeep')
