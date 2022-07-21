import dash
# from dash import dcc, html
import dash_core_components as dcc
import dash_html_components as html
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

app.layout = html.Div([
    dcc.Graph(
        id='heatmap',
        style={"width":"50%", "height": "700px"},
        figure=fig
    ),
])

@app.callback(
    dash.dependencies.Output('heatmap', 'figure'),)
def callback_color():
    fig = go.Figure(go.Densitymapbox(lat=quakes.Latitude, lon=quakes.Longitude, z=quakes.Magnitude,
                                     radius=10))
    fig.update_layout(mapbox_style="stamen-terrain", mapbox_center_lon=180)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig
