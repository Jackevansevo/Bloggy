from flask import (
    render_template,
    send_from_directory,
    request,
    redirect,
    url_for
)
from sqlalchemy import literal

from bloggy import app, db
from bloggy.forms import PostForm
from bloggy.models import Tag, Post, get_or_create

import os


@app.route('/')
def index():
    return render_template('index.html')


def show_posts(posts):
    """Help function to show posts"""
    return render_template('post_list.html', posts=posts)


@app.route('/posts')
def posts():
    if request.args.get('title'):
        return search_posts(request.args['title'])
    return show_posts(Post.query.all())


@app.route('/posts/<string:search_string>', methods=['GET', 'POST'])
def search_posts(search_string):
    posts = Post.query.filter(literal(search_string).contains(Post.title))
    return show_posts(posts)


@app.route('/posts/<int:post_id>')
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post_detail.html', post=post)


@app.route('/posts/edit/<int:post_id>', methods=['GET', 'POST'])
def post_update(post_id):
    post = Post.query.get_or_404(post_id)
    tags = ",".join([str(t) for t in post.tags])
    form = PostForm(title=post.title, markdown=post.markdown, tags=tags)
    # [TODO] Clear the tag relationship before creating new tags
    if form.validate_on_submit():
        post.tilte = form.title.data
        post.markdown = form.markdown.data
        for tag in form.tags.data.split(','):
            post.tags.append(get_or_create(db.session, Tag, name=tag))
        db.session.commit()
        return redirect(post.url)
    return render_template('post_update.html', form=form)


@app.route('/posts/new', methods=['GET', 'POST'])
def post_create():
    form = PostForm(request.form)
    if form.validate_on_submit():
        post = Post(form.title.data, form.markdown.data, True)
        for tag in form.tags.data.split(','):
            post.tags.append(get_or_create(db.session, Tag, name=tag))
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('posts'))
    return render_template('post_create.html', form=form)


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/projects')
def projects():
    return render_template('projects.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'), 'favicon.ico')


@app.template_filter('datetime')
def datetimeformat(value, format='%H:%M / %d-%m-%Y'):
    return value.strftime(format)
