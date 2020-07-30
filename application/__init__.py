import os

from flask import Flask
from flask_migrate import Migrate
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

from application.config import ConfigDevelopment, ConfigRealise


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'app.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_object(ConfigDevelopment)
        # app.config.from_pyfile('config_deploying.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_object(ConfigRealise)
        # app.config.from_pyfile('config_testing.py', silent=True)

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

    cur_app = create_app()

    # FIXME: Comment, please, if not DEBUG mode needed!!!
    cur_app.config['ENV'] = 'development'
    cur_app.config['DEBUG'] = True
    cur_app.config['TESTING'] = True
    cur_app.config['MAIL_ON_ERROR'] = False

    cur_app.run(debug=True, host='0.0.0.0', port=8001, threaded=True, use_reloader=True)
