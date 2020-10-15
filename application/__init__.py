import os

from flask import Flask
from flask_migrate import Migrate
from flask_session import Session, SqlAlchemySessionInterface

import dash
import dash_html_components as html
from dash.dependencies import Input, Output

from application.models import db
from application.homepage import dcc, dbc
from application.homepage import Homepage, App

migrate = Migrate()
sess = Session()


def create_app(test_config=None):

    # create and configure the app
    server = Flask(__name__, instance_relative_config=True)

    # configure application
    if test_config == 'dev':
        server.config.from_object('application.config.DevelopmentConfig')
    elif test_config is None or test_config == 'test':
        server.config.from_object('application.config.TestingConfig')
    elif test_config == 'prod':
        server.config.from_object('application.config.ProductionConfig')

    db.init_app(server)
    sess.init_app(server)
    SqlAlchemySessionInterface(server, db, "sessions", "sess_")
    migrate.init_app(server, db)

    # ensure the instance folder exists
    try:
        os.makedirs(server.instance_path)
    except OSError:
        pass

    # Dash initialize
    app = dash.Dash(
        __name__,
        server=server,
        external_stylesheets=[dbc.themes.UNITED],
        routes_pathname_prefix='/'
    )

    app.config.suppress_callback_exceptions = True
    app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content')
    ])

    # app.layout = html.Div("My Dash Ionosphere app")
    # app.layout = Homepage()

    @server.route('/hello')
    def hello():
        return 'Hello, Only Flask Ionosphere!'

    @app.callback(Output('page-content', 'children'),
                  [Input('url', 'pathname')])
    def display_page(pathname):
        if pathname == '/time-series':
            return App()
        else:
            return Homepage()

    return server


if __name__ == "__main__":
    application = create_app()
    # application = create_app('dev')
    # application = create_app('prod')

    application.run(debug=True, host='0.0.0.0', port=8001, threaded=True, use_reloader=True)
