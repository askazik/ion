### Data
import pandas as pd
import pickle

### Graphing
import plotly.graph_objects as go

import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
from dash.dependencies import Output, Input

from application.navbar import Navbar


df = pd.read_csv(
    'https://gist.githubusercontent.com/joelsewhere/f75da35d9e0c7ed71e5a93c10c52358d/raw/d8534e2f25495cc1de3cd604f952e8cbc0cc3d96/population_il_cities.csv')
df.set_index(df.iloc[:, 0], drop=True, inplace=True)
df = df.iloc[:, 1:]


def Header():
    header = html.H3(
        'Select the name of an Illinois city to see its population!'
    )
    return header


def Dropdown():

    options = [{'label': x.replace(', Illinois', ''), 'value': x} for x in df.columns]
    dropdown = html.Div(dcc.Dropdown(
        id='pop_dropdown',
        options=options,
        value='Abingdon city, Illinois'
    ))
    return dropdown


def Output():
    output = html.Div(id='output',
                      children=[],
                      )
    return output


def Body():
    body = dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H2("Heading"),
                            html.P(
                                """\
       Donec id elit non mi porta gravida at eget metus.Fusce dapibus, tellus ac cursus commodo, tortor mauris condimentumnibh, ut fermentum massa justo sit amet risus. Etiam porta semmalesuada magna mollis euismod. Donec sed odio dui. Donec id elit nonmi porta gravida at eget metus. Fusce dapibus, tellus ac cursuscommodo, tortor mauris condimentum nibh, ut fermentum massa justo sitamet risus. Etiam porta sem malesuada magna mollis euismod. Donec sedodio dui."""
                            ),
                            dbc.Button("View details", color="secondary"),
                        ],
                        md=4,
                    ),
                    dbc.Col(
                        [
                            html.H2("Graph"),
                            dcc.Graph(
                                figure={"data": [{"x": [1, 2, 3], "y": [1, 4, 9]}]}
                            ),
                        ]
                    ),
                ]
            )
        ],
        className="mt-4",
    )

    return body


def build_graph(city):
    data = [
        go.Scatter(x=df.index, y=df[city], marker={'color': 'orange'})]
    graph = dcc.Graph(
        figure={
            'data': data,
            'layout': go.Layout(
                title='{} Population Change'.format(city),
                yaxis={'title': 'Population'},
                hovermode='closest'
            )
        }
    )

    return graph


def Homepage():

    layout = html.Div([
        Navbar(),
        Body()
    ])

    return layout


def App():

    layout = html.Div([
        Navbar(),
        Header(),
        Dropdown(),
        Output()
    ])

    return layout

