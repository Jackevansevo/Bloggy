from config import config
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import click
import os

app = Flask(__name__)
app.config.from_object(config[os.getenv('FLASK_CONFIG', 'default')])

# Initialize Database
db = SQLAlchemy()
db.init_app(app)


@app.cli.command()
def clean():
    """Removes and recreates database."""
    os.remove('db.sqlite3')
    db.create_all()


import bloggy.views, bloggy.models # noqa
