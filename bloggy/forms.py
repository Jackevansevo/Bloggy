from flask_wtf import FlaskForm
from wtforms import StringField, TextField
from wtforms.validators import DataRequired
from string import capwords

from .models import Post


class PostForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    markdown = TextField('markdown', validators=[DataRequired()])
    tags = TextField('tags')
