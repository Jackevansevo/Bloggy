from flask import url_for
from flask_login import UserMixin
from markdown2 import markdown as toHTML
from slugify import slugify
from sqlalchemy import desc
from sqlalchemy.ext.hybrid import hybrid_property

from bloggy import bcrypt, db

tags = db.Table(
    'tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
)


class Author(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    forename = db.Column(db.String(64))
    surname = db.Column(db.String(64))
    email = db.Column(db.String(255), unique=True)
    _password = db.Column(db.String(255))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def is_correct_password(self, plaintext):
        return bcrypt.check_password_hash(self._password, plaintext)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def _set_password(self, plaintext):
        self._password = bcrypt.generate_password_hash(plaintext)

    def __repr__(self):
        return "<Author: {}>".format(str(self))

    def __str__(self):
        return "{} {}".format(self.forename, self.surname)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), index=True, unique=True)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'))
    markdown = db.Column(db.Text, index=True)
    read_estimate = db.Column(db.Float)
    body = db.Column(db.Text)
    published = db.Column(db.Boolean, default=True)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    slug = db.Column(db.String(64))
    tags = db.relationship(
        'Tag', secondary=tags, backref=db.backref('posts', lazy='dynamic')
    )

    __mapper_args__ = {
        "order_by": desc('created_on')
    }

    @property
    def url(self):
        return url_for('post_detail', slug=self.slug)

    def __repr__(self):
        return '<Post %r>' % (self.title)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    icon = db.Column(db.String(20), default='tag')
    colour = db.Column(db.String(20), default='gray')

    def __repr__(self):
        return "<Tag: {}>".format(self.name)

    def __str__(self):
        return self.name


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(120))
    name = db.Column(db.String(120))
    description = db.Column(db.Text)


@db.event.listens_for(Post, "after_insert")
@db.event.listens_for(Post, "after_update")
def after_insert_listener(mapper, connection, target):
    post_table = Post.__table__
    options = {'fenced-code-blocks'}
    connection.execute(
        post_table.update().
        where(post_table.c.id == target.id).
        values(
            body=toHTML(target.markdown, extras=options),
            slug=slugify(target.title, to_lower=True),
            read_estimate=len(target.markdown.split()) / 275
        )
    )


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance
