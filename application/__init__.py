import os

from flask import Flask
from flask_migrate import Migrate
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

from application.config import ProductionConfig, DevelopmentConfig, TestingConfig


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_object(ProductionConfig)
    elif test_config == 'dev':
        # load the test config if passed in
        app.config.from_object(DevelopmentConfig)

        path = os.path.join(app.instance_path, 'dev.sqlite')
        SQLALCHEMY_DATABASE_URI = 'sqlite:////{0}:memory:'.format(path)
        app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    elif test_config == 'test':
        app.config.from_object(TestingConfig)

        path = os.path.join(app.instance_path, 'test.sqlite')
        SQLALCHEMY_DATABASE_URI = 'sqlite:////{0}:memory:'.format(path)
        app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # connect to db
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)

    # use session
    sess = Session()
    sess.init_app(app)

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, Ionosphere!'

    return app


if __name__ == "__main__":

    cur_app = create_app('test')

    # FIXME: Comment, please, if not DEBUG mode needed!!!
    cur_app.config['ENV'] = 'development'
    cur_app.config['DEBUG'] = True
    cur_app.config['TESTING'] = True
    cur_app.config['MAIL_ON_ERROR'] = False

    cur_app.run(debug=True, host='0.0.0.0', port=8001, threaded=True, use_reloader=True)
