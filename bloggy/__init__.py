from config import config
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy

import os

app = Flask(__name__)
app.config.from_object(config[os.getenv('FLASK_CONFIG', 'default')])


# Initialize Database
db = SQLAlchemy()
db.init_app(app)

# Bcrypt Encryption
bcrypt = Bcrypt(app)

# Flask Mail
mail = Mail(app)

# Flask Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"


@app.cli.command()
def clean():
    """Removes and recreates database."""
    os.remove('db.sqlite3')
    db.create_all()


import bloggy.views, bloggy.models # noqa
