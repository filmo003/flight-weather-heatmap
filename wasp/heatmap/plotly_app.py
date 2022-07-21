import dash
from dash.dependencies import Input, Output
from dash import dcc, html
# import dash_core_components as dcc
# import dash_html_components as html
import dash_bootstrap_components as dbc
import os

from django_plotly_dash import DjangoDash

app = DjangoDash('SimpleExample')   # replaces dash.Dash

import pandas as pd
quakes = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/earthquakes-23k.csv')
df = pd.read_csv(os.getcwd() + "\\heatmap\\mockdata.csv")

import plotly.graph_objects as go

fig = go.Figure(go.Densitymapbox(lat=df['latitude'], lon=df['longitude'], z=df['cancelPercent'], radius=20, text=df['base']))
fig.update_layout(mapbox_style="stamen-terrain", mapbox_center_lon=180)
fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

months = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]

app.layout = html.Div([

    dbc.Row([
        dbc.Col([
            dcc.Graph(
                    id='heatmap',
                    style={"width":"50%", "height": "700px"},
                    figure=fig
            ),
        ]),
        dbc.Col([
            dcc.Slider(marks=months,
                       value=2,
                       min=0,
                       max=11,
                       step=1,
                       id='my-slider'
            ),
        ]),
    ]),
    dbc.Row([]),




    html.Div(id='slider-output-container', style={"width":"50%"},)
])

@app.callback(
    Output('heatmap', 'figure'),
    Output('slider-output-container', 'children'),
    Input('my-slider', 'value')
)
def callback_color(value):
    fig = go.Figure(
        go.Densitymapbox(lat=df['latitude'], lon=df['longitude'], z=df['cancelPercent'], radius=20, text=df['base']))
    fig.update_layout(mapbox_style="stamen-terrain", mapbox_center_lon=180)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig, months[value]
