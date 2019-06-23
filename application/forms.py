from flask_wtf import Form
from wtforms import SubmitField


class EnterGenerate(Form):
    submit = SubmitField(label='Generate NPC')