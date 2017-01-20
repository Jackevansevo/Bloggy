import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret key'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
    BCRYPT_LOG_ROUNDS = 12


class DevelopmentConfig(Config):
    MAIL_SERVER = "mail.evans.gb.net"
    MAIL_PORT = 110
    MAIL_PASSWORD = "VTX1000!"
    MAIL_USERNAME = "jack"
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(
        basedir, 'db.sqlite3')


class TestingConfig(Config):
    TESTING = True


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
