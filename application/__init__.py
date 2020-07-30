import os

from flask import Flask
from flask_migrate import Migrate
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

from application.config import ProductionConfig, DevelopmentConfig, TestingConfig


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if test_config == 'dev' or test_config == 'test':
        if test_config == 'dev':
            app.config.from_object(DevelopmentConfig)
        if test_config == 'test':
            app.config.from_object(TestingConfig)

        path = os.path.join(app.instance_path, 'dev.sqlite')
        SQLALCHEMY_DATABASE_URI = 'sqlite:////{0}'.format(path)
        app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    elif test_config is None or test_config == 'prod':
        app.config.from_object(ProductionConfig)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # connect to db
    app.db = SQLAlchemy(app)
    app.migrate = Migrate(app, app.db)

    with app.app_context():
        import application.models

    # use session
    sess = Session()
    sess.init_app(app)
    # app.session_interface.db.create_all()

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, Ionosphere!'

    return app


if __name__ == "__main__":

    cur_app = create_app('test')
    cur_app.run(debug=True, host='0.0.0.0', port=8001, threaded=True, use_reloader=True)
