import os
import datetime
import configparser
import sys

basedir = os.path.abspath(os.path.dirname(__file__))
topdir = os.path.abspath(os.path.join(basedir, '..'))

CONFIG_INI = 'config.ini'
config = configparser.ConfigParser()
config.read(os.path.join(basedir, CONFIG_INI))
LOGGING_FILE = os.path.join(topdir, config['FILES']['logging_file'])


def create_recreate_session(app, logging):
    from sqlalchemy.exc import OperationalError
    from time import sleep
    while True:
        try:
            app.session_interface.db.create_all()
        except OperationalError as ex:
            logging.error('Failed.', exc_info=ex)
            sleep(60)
        else:
            break


class Config(object):
    DEBUG = False
    TESTING = False
    DATABASE_URI = 'sqlite:///:memory:'


class ProductionConfig(Config):

    TEMPLATES_AUTO_RELOAD = False

    PERMANENT_SESSION_LIFETIME = datetime.timedelta(hours=6)
    SESSION_REFRESH_EACH_REQUEST = True

    SECRET_KEY = os.urandom(64)
    SESSION_TYPE = 'sqlalchemy'

    dialect = config['DATABASE']['dialect']
    driver = config['DATABASE']['driver']
    user = config['DATABASE']['user']
    password = config['DATABASE']['password']
    if "builds/math" in sys.argv[0]:
        host = 'mysql'
    else:
        host = config['DATABASE']['host']
    port = config['DATABASE']['port']
    db = config['DATABASE']['db']

    SUPPORTED_LANGUAGES = {"ru": "Russian", "en": "English"}
    BABEL_DEFAULT_TIMEZONE = "UTC"

    SQLALCHEMY_DATABASE_URI = \
        dialect + '+' + driver + '://' + user + ':' + password + '@' + host + ':' + port + '/' + db

    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(ProductionConfig):
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(hours=12)
    SECRET_KEY = 'dev'


class TestingConfig(DevelopmentConfig):
    TESTING = True
