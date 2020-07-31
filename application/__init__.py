import os

from flask import Flask
from flask_migrate import Migrate
from flask_session import Session, SqlAlchemySessionInterface

from application.models import db

migrate = Migrate()
sess = Session()


def create_app(test_config=None):

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    # configure application
    if test_config == 'dev':
        app.config.from_object('application.config.DevelopmentConfig')
    elif test_config is None or test_config == 'test':
        app.config.from_object('application.config.TestingConfig')
    elif test_config == 'prod':
        app.config.from_object('application.config.ProductionConfig')

    db.init_app(app)
    sess.init_app(app)
    SqlAlchemySessionInterface(app, db, "sessions", "sess_")
    migrate.init_app(app, db)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/hello')
    def hello():
        return 'Hello, Ionosphere!'

    return app


if __name__ == "__main__":
    application = create_app()
    # application = create_app('dev')
    # application = create_app('prod')

    application.run(debug=True, host='0.0.0.0', port=8001, threaded=True, use_reloader=True)
