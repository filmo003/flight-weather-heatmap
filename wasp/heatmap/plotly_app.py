from dash import dcc, html
import os
from django_plotly_dash import DjangoDash
import pandas as pd
import plotly.graph_objects as go

months = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]



import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.express as px

# Iris bar figure
def drawFigure(df):
    return  html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(
                    figure=px.bar(
                        df, x="sepal_width", y="sepal_length", color="species"
                    ).update_layout(
                        template='plotly_dark',
                        plot_bgcolor= 'rgba(0, 0, 0, 0)',
                        paper_bgcolor= 'rgba(0, 0, 0, 0)',
                    ),
                    config={
                        'displayModeBar': False
                    }
                )
            ])
        ),
    ])

# Text field
def drawText(text):
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                html.Div([
                    html.H2(text),
                ], style={'textAlign': 'center'})
            ])
        ),
    ])

# Data
df1 = px.data.iris()
df_heatmap = pd.read_csv(os.getcwd() + "/heatmap/mockdata.csv")
df_aircraft = pd.read_csv(os.getcwd() + "/heatmap/aircraftdata.csv")
# quakes = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/earthquakes-23k.csv')

# Heatmap
def drawHeatmap(df):
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(id='heatmap',
                    figure=go.Figure(
                        go.Densitymapbox(lat=df['latitude'], lon=df['longitude'], z=df['cancelPercent'], radius=20, text=df['base']))
                    .update_layout(
                        mapbox_style="stamen-terrain", mapbox_center_lon=180, margin={"r": 0, "t": 0, "l": 0, "b": 0}
                    ),
                    config={
                        'displayModeBar': False
                    }
                ),
                dcc.Slider(marks=months,
                           value=2,
                           min=0,
                           max=11,
                           step=1,
                           id='month-slider'
                ),
                html.Div(id='slider-output-container', style={"width":"50%"},)


            ])
        ),
    ])

# Aircraft Dropdown
def drawAircraftDropdown(df):
    aircraft = ["Globalhawk", "C-130"]

    return html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Dropdown(
                    aircraft,
                    placeholder="Select an aircraft",
                    id='aircraft-dropdown',
                ),
                html.Div(id='aircraft-dropdown-output-container', style={"width": "50%"}, ),
                dbc.Row([
                    dbc.Col(["Max Crosswind:"], width=6),
                    dbc.Col([
                        dcc.Input(
                            id="crosswind",
                            type="number",
                            placeholder=df.loc[df['aircraft'] == "C-130"]['crosswind'],
                        )
                    ], width=6),
                ]),
                dbc.Row([
                    dbc.Col(["Max Crosswind:"], width=6),
                    dbc.Col([
                        dcc.Input(
                            id="crosswind",
                            type="number",
                            placeholder=df.loc[df['aircraft'] == "C-130"]['crosswind'],
                        )
                    ], width=6),
                ]),
                dbc.Row([
                    dbc.Col(["Max Crosswind:"], width=6),
                    dbc.Col([
                        dcc.Input(
                            id="crosswind",
                            type="number",
                            placeholder=df.loc[df['aircraft'] == "C-130"]['crosswind'],
                        )
                    ], width=6),
                ]),


            ])
        ),
    ])

# Initialize Figure
fig = go.Figure()

# Build App
app = DjangoDash('SimpleExample', external_stylesheets=[dbc.themes.SLATE])

app.layout = html.Div([
    dbc.Card(
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    drawText("Weather Awareness Sorty Planner")
                ], width=6),
                dbc.Col([
                    drawText("(WASP)")
                ], width=6),
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    drawHeatmap(df_heatmap),
                ], width=8),
                dbc.Col([
                    drawAircraftDropdown(df_aircraft)
                ], width=4),
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    drawFigure(df1)
                ], width=9),
                dbc.Col([
                    drawFigure(df1)
                ], width=3),
            ], align='center'),
        ]), color = 'dark'
    )
])
@app.callback(
    Output('heatmap', 'figure'),
    Output('slider-output-container', 'children'),
    Output('aircraft-dropdown-output-container', 'children'),
    Input('month-slider', 'value'),
    Input('aircraft-dropdown', 'value'),
)
def callback_color(month, aircraft):
    df = df_heatmap
    fig = go.Figure(
        go.Densitymapbox(lat=df['latitude'], lon=df['longitude'], z=df['cancelPercent'], radius=20, text=df['base']))
    fig.update_layout(mapbox_style="stamen-terrain", mapbox_center_lon=180)
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig, months[month], aircraft
# Run app and display result inline in the notebook
# app.run_server(mode='external')