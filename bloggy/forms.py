from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import BooleanField, PasswordField, StringField, TextField


from wtforms.validators import DataRequired, Email

from bloggy.models import Author


class PostForm(FlaskForm):
    title = StringField('title', validators=[DataRequired()])
    markdown = TextField('markdown', validators=[DataRequired()])
    published = BooleanField('published')
    tags = TextField('tags')


class ContactForm(FlaskForm):
    message = TextField('content', validators=[DataRequired()])


class TagForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    icon = StringField('icon', validators=[DataRequired()])
    colour = StringField('colour', validators=[DataRequired()])


class ProjectForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    description = TextField('description', validators=[DataRequired()])
    image = FileField(validators=[FileRequired()])


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

    def validate(self):
        rv = FlaskForm.validate(self)
        if not rv:
            return False
        author = Author.query.filter_by(email=self.email.data).first()
        if author is None:
            error_msg = 'Unable to find author with matching email in system'
            self.email.errors.append(error_msg)
            return False

        if not author.is_correct_password(self.password.data):
            self.password.errors.append('Invalid password')
            return False

        self.author = author
        return True
