import os

from flask import Flask
from flask_migrate import Migrate
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy

from application.config import ProductionConfig, DevelopmentConfig, TestingConfig

db = SQLAlchemy()
migrate = Migrate()
sess = Session()


def create_app(test_config=None):

    # create and configure the app
    app = Flask(__name__)

    # configure application
    if test_config == 'dev':
        app.config.from_object(DevelopmentConfig)
    elif test_config is None or test_config == 'test':
        app.config.from_object(TestingConfig)
    elif test_config == 'prod':
        app.config.from_object(ProductionConfig)

    # attach needed instances
    sess.init_app(app)
    db.init_app(app)
    app.db = db
    migrate.init_app(app, db)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # check the database models (added for get models changes)
    with app.app_context():
        import application.models

    app.session_interface.db.create_all()

    @app.route('/hello')
    def hello():
        return 'Hello, Ionosphere!'

    return app


application = create_app('test')

if __name__ == "__main__":
    application.run(debug=True, host='0.0.0.0', port=8001, threaded=True, use_reloader=True)
