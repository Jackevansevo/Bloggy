from flask import url_for
from sqlalchemy import desc
from sqlalchemy import event

from markdown2 import markdown as toHTML

from bloggy import db

tags = db.Table(
    'tags',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
)

posts = db.Table(
    'posts',
    db.Column('author_id', db.Integer, db.ForeignKey('author.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
)


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    forename = db.Column(db.String(64))
    surname = db.Column(db.String(64))
    posts = db.relationship(
        'Post', secondary=posts, backref=db.backref('authors', lazy='dynamic')
    )


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), index=True, unique=True)
    markdown = db.Column(db.Text, index=True)
    body = db.Column(db.Text)
    published = db.Column(db.Boolean, default=True)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    tags = db.relationship(
        'Tag', secondary=tags, backref=db.backref('posts', lazy='dynamic')
    )

    __mapper_args__ = {
        "order_by": desc('created_on')
    }

    @property
    def url(self):
        return url_for('post_detail', post_id=self.id)

    def __init__(self, title, markdown, published):
        self.title = title
        self.markdown = markdown
        self.published = published

    def __repr__(self):
        return '<Post %r>' % (self.title)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True)
    icon = db.Column(db.String(20), unique=True)
    colour = db.Column(db.String(20), unique=True)

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
        values(body=toHTML(target.markdown, extras=options))
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
