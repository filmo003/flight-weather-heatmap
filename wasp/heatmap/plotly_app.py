from dash import dcc, html
import os
from django_plotly_dash import DjangoDash
import pandas as pd
import plotly.graph_objects as go

import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, ALL
import plotly.express as px
from .API.backendAPI import API
import numpy as np
import colour as color
Color = color.Color
from matplotlib.colors import LinearSegmentedColormap

token = "pk.eyJ1IjoiYWx5c2FrMTAiLCJhIjoiY2w1dmhhZGhrMDlyNDNobnoxMnpoMG1ubiJ9.nJeJvSZfuDdTBjtFfqrwkg"
red = Color("red")
colorscale = list(red.range_to(Color("green"),10))
base_colors = []

cmap_name = "green-red"
colors = [(1, 0, 0), (0, 1, 0)]
n_bin = 100
cm = LinearSegmentedColormap.from_list(
        cmap_name, colors, N=n_bin)

months = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]


api = API(os.getcwd() + "/heatmap/monthly_f35_weather_canx.csv", useMemory = False, deleteExisting = False)
connection = api.createDatabase()

#This is how you cet Canx data for a specific base. Returns {Name, Month, Canx}


#This is how you can query all base info. Returns {Name, Latitude, Longitude}
bases = api.getBases()
for base in bases: print(base)

#This is how you can create your own custom query. Returns all results
# custom = api.executeQuery("SELECT * FROM weatherData")
# print(custom)

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
df_heatmap = pd.read_csv(os.getcwd() + "/heatmap/monthly_f35_weather_canx.csv")
df_heatmap['Marker Size'] = pd.Series([3 for x in range(len(df_heatmap.index))])
df_aircraft = pd.read_csv(os.getcwd() + "/heatmap/aircraftdata.csv")
df_filtered_heatmap = df_heatmap.loc[df_heatmap['month'] == 1]
df_base = df_heatmap.loc[df_heatmap['base_text'] == "BEALE"]
selected_base = "BEALE AFB"
# Heatmap
def drawHeatmap(df):
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(id='heatmap',
                          figure=px.scatter_mapbox(df_filtered_heatmap, lat="latitude", lon="longitude", hover_name="base_text", hover_data=["month", "Canx"],
                        color="Canx", zoom=3, height=700, color_continuous_scale='Bluered', size="Marker Size")
                            .update_layout(mapbox_style="dark", mapbox_accesstoken=token)
                          .update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
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
                html.Div(id='max-crosswind', style={"width": "50%"}, ),
                html.Div(id='max-temp', style={"width": "50%"}, ),
                html.Div(id='min-temp', style={"width": "50%"}, ),
            ])
        ),
    ])

# Aircraft Dropdown
def drawBaseDropdown(bases):
    bases = np.array(bases)[:,0]
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Dropdown(
                    bases,
                    placeholder="Select a base",
                    id='base-dropdown',
                ),
                html.Div(id='base-dropdown-output-container', style={"width": "50%"}, ),
            ])
        ),
    ])

def drawBaseHistogram(df, base="BEALE AFB"):
    canx = np.array(api.getCanx(base))

    df_base = df.loc[df['base_text']==base]
    return html.Div([
        dbc.Card(
            dbc.CardBody([
                dcc.Graph(id='barchart',
                    figure=px.bar(x=canx[:,1], y=canx[:,2], )
                    .update_layout(
                        template='plotly_dark',
                        plot_bgcolor='rgba(0, 0, 0, 0)',
                        paper_bgcolor='rgba(0, 0, 0, 0)',
                    ),
                    config={
                        'displayModeBar': False
                    }
                )
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
                    drawText("Weather Awareness Sortyyy Planner")
                ], width=6),
                dbc.Col([
                    drawText("(WASP)")
                ], width=6),
            ], align='center'),
            html.Br(),
            dbc.Row([
                dbc.Col([
                    drawHeatmap(df_heatmap)
                ], width=8),
                dbc.Col([
                    drawAircraftDropdown(df_aircraft),
                    html.Br(),
                    drawBaseDropdown(bases),
                    drawBaseHistogram(df_heatmap, selected_base),

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
    Output('barchart', 'figure'),
    Output('slider-output-container', 'children'),
    Output('aircraft-dropdown-output-container', 'children'),
    Output('base-dropdown-output-container', 'children'),
    Output('max-crosswind', 'children'),
    Output('max-temp', 'children'),
    Output('min-temp', 'children'),
    Input('month-slider', 'value'),
    Input('aircraft-dropdown', 'value'),
    Input('base-dropdown', 'value'),
)
def callback_color(month, aircraft, base):
    selected_base = base
    df_filtered_heatmap = df_heatmap.loc[df_heatmap['month'] == month+1]

    fig = px.scatter_mapbox(df_filtered_heatmap, lat="latitude", lon="longitude", hover_name="base_text", hover_data=["month", "Canx"],
                        color="Canx", zoom=3, height=700, color_continuous_scale='Bluered', size="Marker Size")

    fig.update_layout(mapbox_style="dark", mapbox_accesstoken=token)

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    canx2 = np.array(api.getCanx(base))
    fig2 = px.bar(x=canx2[:, 1], y=canx2[:, 2], )
    fig2.update_layout(
        template='plotly_dark',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
    )

    try:
        max_crosswind = "Max Crosswind: " + str(df_aircraft.loc[df_aircraft['aircraft'] == aircraft]['crosswind'].array[0])
        max_temp = "Max Temperature: " + str(df_aircraft.loc[df_aircraft['aircraft'] == aircraft]['crosswind'].array[0])
        min_temp = "Min Temperature: " + str(df_aircraft.loc[df_aircraft['aircraft'] == aircraft]['crosswind'].array[0])
    except:
        max_crosswind = "Max Crosswind: "
        max_temp = "Max Temperature: "
        min_temp = "Min Temperature: "
    return fig, fig2, months[month], aircraft, base, max_crosswind, max_temp, min_temp
