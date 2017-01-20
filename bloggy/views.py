from flask import (
    abort,
    flash,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)

from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message

from urllib.parse import urlparse, urljoin

from bloggy import app, db, login_manager, mail
from bloggy.forms import LoginForm, PostForm, ProjectForm, TagForm, ContactForm
from bloggy.models import Author, Tag, Post, get_or_create
from bloggy.serializers import serialize_post


import os


@app.route('/')
def index():
    # [TODO] Eventually remove this
    # [TODO] Migrate to Postgres
    return redirect(url_for('post_list'))


def show_posts(posts):
    """Help function to show posts"""
    return render_template('post_list.html', posts=posts, tags=Tag.query.all())


@app.route('/api/posts/<int:post_id>')
def post_json(post_id):
    post = Post.query.get(post_id)
    return serialize_post(post)


@app.route('/posts')
def post_list():
    if request.args.get('title'):
        posts = Post.query.filter(Post.title.contains(request.args['title']))
        return show_posts(posts)
    return show_posts(Post.query.all())


@app.route('/posts/<string:slug>')
def post_detail(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    return render_template('post_detail.html', post=post)


@app.route('/posts/edit/<string:slug>', methods=['GET', 'POST'])
@login_required
def post_update(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    tags = ",".join([str(t) for t in post.tags])
    form = PostForm(title=post.title, markdown=post.markdown, tags=tags)
    if form.validate_on_submit():
        post.title = form.title.data
        post.markdown = form.markdown.data
        post.tags = []
        for tag in form.tags.data.split(','):
            post.tags.append(get_or_create(db.session, Tag, name=tag))
        db.session.commit()
        flash('Post updated', 'success')
        return redirect(post.url)
    return render_template('post_form.html', form=form)


@app.route('/posts/new', methods=['GET', 'POST'])
@login_required
def post_create():
    form = PostForm(request.form)
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            markdown=form.markdown.data,
            published=form.published.data,
            author_id=current_user.id,
        )
        for tag in filter(None, form.tags.data.split(',')):
            post.tags.append(get_or_create(db.session, Tag, name=tag))
        db.session.add(post)
        db.session.commit()
        flash('Post created', 'success')
        return redirect(url_for('post_list'))
    return render_template('post_form.html', form=form)


@app.route('/posts/delete/<string:slug>', methods=['POST'])
def post_delete(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()
    db.session.delete(post)
    db.session.commit()
    flash('post deleted', 'success')
    return redirect(url_for('post_list'))


@app.route('/tags/edit/<string:tag>', methods=['GET', 'POST'])
def tag_update(tag):
    tag = Tag.query.filter_by(name=tag).first_or_404()
    form = TagForm(obj=tag)
    if form.validate_on_submit():
        tag.name = form.name.data
        tag.icon = form.icon.data
        tag.colour = form.colour.data
        db.session.add(tag)
        db.session.commit()
        flash('Tag Updated', 'success')
        return redirect(url_for('tag_detail', tag=tag))
    return render_template('tag_form.html', form=form)


@app.route('/tags/<string:tag>')
def tag_detail(tag):
    tag = Tag.query.filter_by(name=tag).first_or_404()
    return show_posts(tag.posts.all())


@app.route('/about')
def about():
    form = ContactForm()
    return render_template('about.html', form=form)


@app.route('/contact', methods=['POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        # Send the mail
        msg = Message(
            form.message.data,
            sender="jack@evans.gb.net",
            recipients=["jack@evans.gb.net"]
        )
        # [TODO] Figure out sending mail
        # [TODO] Rate limit mail sending
        # [TODO] Add Recaptcha field
        mail.send(msg)
        flash('Message sent', 'success')
    else:
        flash('Message failed to sent', 'warning')
    return redirect(url_for('about'))


@app.route('/projects')
def projects():
    form = ProjectForm()
    return render_template('projects.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('Already logged in', 'info')
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Author.query.filter_by(email=form.email.data).first_or_404()
        if user.is_correct_password(form.password.data):
            login_user(user)
            next = request.args.get('next')
            if not is_safe_url(next):
                return abort(400)
            flash('Logged in', 'success')
            return redirect(next or url_for('index'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html', form=form)


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out', 'success')
    return redirect(url_for('index'))


@login_manager.user_loader
def load_user(author_id):
    return Author.query.get(author_id)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'), 'favicon.ico')


@app.template_filter('datetime')
def datetimeformat(value, format='%d/%m/%Y - %I:%M %p '):
    return value.strftime(format)
