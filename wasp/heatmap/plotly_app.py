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
from plotly_calplot import calplot
from dotenv import load_dotenv

load_dotenv()

MONTHLY_DATA = "monthly_base_weather_data.csv"
DAILY_DATA = "daily_base_weather_data.csv"
AIRCRAFT_DATA = "aircraftdata.csv"

token = os.getenv("MAPBOX_TOKEN")
red = Color("red")
colorscale = list(red.range_to(Color("green"), 10))
base_colors = []

cmap_name = "green-red"
colors = [(1, 0, 0), (0, 1, 0)]
n_bin = 100
cm = LinearSegmentedColormap.from_list(cmap_name, colors, N=n_bin)

months = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


api = API(
    os.getcwd() + "/heatmap/base_weather_data.csv",
    useMemory=False,
    deleteExisting=False,
)
connection = api.createDatabase()

# This is how you cet Canx data for a specific base. Returns {Name, Month, Canx}


# This is how you can create your own custom query. Returns all results
# custom = api.executeQuery("SELECT * FROM weatherData")
# print(custom)


# Iris bar figure
def drawFigure(df):
    return html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        dcc.Graph(
                            figure=px.bar(
                                df, x="sepal_width", y="sepal_length", color="species"
                            ).update_layout(
                                template="plotly_dark",
                                plot_bgcolor="rgba(0, 0, 0, 0)",
                                paper_bgcolor="rgba(0, 0, 0, 0)",
                            ),
                            config={"displayModeBar": False},
                        )
                    ]
                )
            ),
        ]
    )


# Text field
def drawText(text):
    return html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Div(
                            [
                                html.H2(text),
                            ],
                            style={"textAlign": "center"},
                        )
                    ]
                )
            ),
        ]
    )


# Data
df1 = px.data.iris()
data_folder = os.path.join(os.getcwd(), 'data')
monthly_data_file = os.path.join(data_folder, MONTHLY_DATA)
df_heatmap = pd.read_csv(monthly_data_file)
daily_data_file = os.path.join(data_folder, DAILY_DATA)
df_heatmap_daily = pd.read_csv(daily_data_file)
df_heatmap["Marker Size"] = pd.Series([3 for x in range(len(df_heatmap.index))])
aircraft_data_file = os.path.join(data_folder, AIRCRAFT_DATA)
df_aircraft = pd.read_csv(aircraft_data_file)
df_filtered_heatmap = df_heatmap.loc[df_heatmap["month"] == 1]
df_base = df_heatmap.loc[df_heatmap["base_text"] == "BEALE"]
selected_base = "BEALE AFB"
selected_aircraft = df_aircraft["aircraft"][0]
num_sorties = 100

# This is how you can query all base info. Returns {Name, Latitude, Longitude}
bases = api.getBases()


# bases = df_filtered_heatmap['base_text']
# for base in bases: print(base)
# Heatmap
def drawHeatmap(df_filtered_heatmap):
    df_filtered_heatmap = df_filtered_heatmap.loc[
        df_heatmap["aircraft"] == selected_aircraft
    ]
    return html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        dcc.Graph(
                            id="heatmap",
                            figure=px.scatter_mapbox(
                                df_filtered_heatmap,
                                lat="latitude",
                                lon="longitude",
                                hover_name="base_text",
                                hover_data=["Canx"],
                                color="Canx",
                                zoom=3,
                                height=650,
                                color_continuous_scale="Bluered",
                                size="Marker Size",
                                color_continuous_midpoint=0.15,
                            )
                            .update_layout(
                                mapbox_style="dark",
                                mapbox_accesstoken=token,
                                coloraxis_showscale=False,
                            )
                            .update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}),
                        ),
                        dcc.Slider(
                            marks=months,
                            value=2,
                            min=0,
                            max=11,
                            step=1,
                            id="month-slider",
                        ),
                        html.Div(
                            id="slider-output-container",
                            style={"width": "50%"},
                        ),
                    ]
                )
            ),
        ],
        style={"height": "70%"},
    )


def drawBasemap(df):
    return html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        dcc.Graph(
                            id="basemap",
                            figure=px.scatter_mapbox(
                                df,
                                lat="latitude",
                                lon="longitude",
                                hover_name="base_text",
                                hover_data=["month", "Canx"],
                                color_discrete_sequence=["white"],
                                zoom=12,
                                height=300,
                            )
                            .update_layout(
                                mapbox_style="dark",
                                mapbox_accesstoken=token,
                                coloraxis_showscale=False,
                            )
                            .update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}),
                        ),
                    ]
                )
            ),
        ]
    )


# Aircraft Dropdown
def drawAircraftDropdown(df):
    aircraft = ["global-Hawk", "f-35"]

    return html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        dcc.Dropdown(
                            aircraft,
                            placeholder="Select an aircraft",
                            id="aircraft-dropdown",
                        ),
                        # html.Div(id='aircraft-dropdown-output-container', style={"width": "50%"}, ),
                        html.Div(
                            id="crosswind",
                            style={"width": "50%"},
                        ),
                        html.Div(
                            id="altitude",
                            style={"width": "50%"},
                        ),
                        html.Div(
                            id="ceiling",
                            style={"width": "50%"},
                        ),
                        html.Div(
                            id="rcr",
                            style={"width": "100%"},
                        ),
                        html.Div(
                            id="takeoff-time",
                            style={"width": "50%"},
                        ),
                        html.Div(
                            id="landing-time",
                            style={"width": "50%"},
                        ),
                    ]
                )
            ),
        ]
    )


def drawNumSortiesField():
    aircraft = ["global-Hawk", "f-35"]

    return html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        dbc.Col([html.Div(["Number of Sorties: "])], width=6),
                        dbc.Col(
                            [
                                dcc.Input(
                                    id="num-sorties",
                                    type="number",
                                    placeholder=100,
                                )
                            ],
                            width=6,
                        ),
                    ]
                )
            ),
        ]
    )


# Base Dropdown
def drawBaseDropdown(bases):
    # bases = np.array(bases)[:,0]
    return html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Div(["Base: "]),
                        dcc.Dropdown(
                            bases["base_text"],
                            placeholder="Select a base",
                            id="base-dropdown",
                        ),
                    ]
                )
            ),
        ]
    )


def drawBaseHistogram(base="BEALE AFB"):
    canx = api.getCanx(base, selected_aircraft)
    sorties_to_schedule = 1 - canx["canx"]
    sorties_to_schedule /= sorties_to_schedule.sum()
    sorties_to_schedule *= num_sorties
    return html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        html.Div(
                            [
                                html.H2("Cancel Probability"),
                            ],
                            style={"textAlign": "center"},
                        ),
                        dcc.Graph(
                            id="barchart",
                            figure=px.bar(
                                x=canx["month"],
                                y=sorties_to_schedule,
                                height=250,
                                labels={
                                    "Month",
                                    "Cancellation Probability",
                                },
                                title="Monthly Cancellations",
                            ).update_layout(
                                template="plotly_dark",
                                plot_bgcolor="rgba(0, 0, 0, 0)",
                                paper_bgcolor="rgba(0, 0, 0, 0)",
                                margin=dict(l=0, r=0, t=0, b=0),
                            ),
                            config={"displayModeBar": False},
                        ),
                    ]
                )
            ),
        ]
    )


def drawCalendar(combined_df):
    combined = combined_df.loc[
        (combined_df["base_text"] == selected_base)
        & (combined_df["aircraft"] == selected_aircraft)
    ]
    # date range from start date to end date and random
    # column named value using amount of days as shape
    combined["Datetime"] = (
        "2022" + "-" + combined["month"].astype(str) + "-" + combined["day"].astype(str)
    )
    combined["Datetime"] = pd.to_datetime(combined["Datetime"], errors="coerce")
    combined = combined.dropna()
    return html.Div(
        [
            dbc.Card(
                dbc.CardBody(
                    [
                        dcc.Graph(
                            id="calendar",
                            figure=calplot(
                                combined,
                                x="Datetime",
                                y="Canx",
                                dark_theme=True,
                                colorscale="reds",
                                total_height=300,
                            ),
                        )
                    ]
                )
            ),
        ]
    )


# Initialize Figure
fig = go.Figure()

# Build App
app = DjangoDash("SimpleExample", external_stylesheets=[dbc.themes.SLATE])

app.layout = html.Div(
    [
        dbc.Card(
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [drawText("Weather Awareness Sortie Planner")], width=6
                            ),
                            dbc.Col([drawText("(WASP)")], width=6),
                        ],
                        align="center",
                    ),
                    html.Br(),
                    dbc.Row(
                        [
                            dbc.Col(
                                [drawHeatmap(df_filtered_heatmap)],
                                width=7,
                                style={"height": "70%"},
                            ),
                            dbc.Col(
                                [
                                    drawBaseDropdown(bases),
                                    drawBasemap(
                                        df_filtered_heatmap.loc[
                                            df_filtered_heatmap["base_text"]
                                            == selected_base
                                        ]
                                    ),
                                    # dbc.Row([
                                    #     dbc.Col([
                                    #         drawAircraftDropdown(df_aircraft),
                                    #         drawNumSortiesField()
                                    #     ]),
                                    #     dbc.Col([drawBaseHistogram(selected_base)]),
                                    # ], no_gutters=True),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                [
                                                    drawAircraftDropdown(df_aircraft),
                                                    drawNumSortiesField(),
                                                ]
                                            ),
                                            dbc.Col([drawBaseHistogram(selected_base)]),
                                        ]
                                    ),
                                ],
                                width=5,
                                style={"height": "70%"},
                            ),
                        ],
                        align="center",
                    ),
                    html.Br(),
                    dbc.Row(
                        [dbc.Col([drawCalendar(df_heatmap_daily)])], align="center"
                    ),
                ]
            ),
            color="dark",
        )
    ]
)


@app.callback(
    Output("heatmap", "figure"),
    Output("barchart", "figure"),
    Output("basemap", "figure"),
    Output("calendar", "figure"),
    Output("slider-output-container", "children"),
    # Output('aircraft-dropdown-output-container', 'children'),
    # Output('base-dropdown-output-container', 'children'),
    Output("crosswind", "children"),
    Output("altitude", "children"),
    Output("ceiling", "children"),
    Output("rcr", "children"),
    Output("takeoff-time", "children"),
    Output("landing-time", "children"),
    Input("month-slider", "value"),
    Input("aircraft-dropdown", "value"),
    Input("num-sorties", "value"),
    Input("base-dropdown", "value"),
)
def callback_color(month, aircraft="global-Hawk", num_sorties=100, base="BEALE AFB"):
    if base != None:
        selected_base = base
    else:
        selected_base = "BEALE AFB"

    if aircraft != None:
        selected_aircraft = aircraft
    else:
        selected_aircraft = "global-Hawk"

    if num_sorties != None:
        num_sorties = num_sorties
    else:
        num_sorties = 100

    df_filtered_heatmap = df_heatmap.loc[df_heatmap["aircraft"] == selected_aircraft]
    df_filtered_heatmap = df_filtered_heatmap.loc[
        df_filtered_heatmap["month"] == month + 1
    ]

    fig = px.scatter_mapbox(
        df_filtered_heatmap,
        lat="latitude",
        lon="longitude",
        hover_name="base_text",
        hover_data=["Canx"],
        color="Canx",
        zoom=3,
        height=650,
        color_continuous_scale="Bluered",
        size="Marker Size",
        color_continuous_midpoint=0.15,
    )

    fig.update_layout(
        mapbox_style="dark", mapbox_accesstoken=token, coloraxis_showscale=False
    )

    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    # canx = api.getCanx(selected_base, selected_aircraft)

    # canx_array = np.array([[1,2,3,4,5,6,7,8,9,10,11,12],[0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]]).T
    # canx = pd.DataFrame(canx_array, columns=['month', 'canx'])

    df_hist = df_heatmap.loc[
        (df_heatmap["base_text"] == selected_base)
        & (df_heatmap["aircraft"] == selected_aircraft)
    ]

    sorties_to_schedule = df_hist["Canx"]
    # sorties_to_schedule/=sorties_to_schedule.sum()
    # sorties_to_schedule*=num_sorties

    # fig2 = px.bar(x=df_hist['month'], y=sorties_to_schedule, labels={
    #                                   "Month",
    #                                   "Cancellation Probability",
    #
    #                               },
    #                               title="Monthly Cancellations")
    months = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    fig2 = go.Figure()
    fig2.add_trace(
        go.Bar(
            x=months,
            y=sorties_to_schedule,
        )
    )
    fig2.update_layout(
        template="plotly_dark",
        plot_bgcolor="rgba(0, 0, 0, 0)",
        paper_bgcolor="rgba(0, 0, 0, 0)",
        margin=dict(l=0, r=0, t=0, b=0),
    )

    fig3 = px.scatter_mapbox(
        df_filtered_heatmap.loc[df_filtered_heatmap["base_text"] == selected_base],
        lat="latitude",
        lon="longitude",
        hover_name="base_text",
        hover_data=["month", "Canx"],
        color_discrete_sequence=["white"],
        zoom=12,
        height=300,
    )
    fig3.update_layout(
        mapbox_style="dark",
        mapbox_accesstoken=token,
        coloraxis_showscale=False,
    )

    fig3.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    combined_df = df_heatmap_daily
    combined = combined_df.loc[
        (combined_df["base_text"] == selected_base)
        & (combined_df["aircraft"] == selected_aircraft)
    ]
    combined["Datetime"] = (
        "2022" + "-" + combined["month"].astype(str) + "-" + combined["day"].astype(str)
    )
    combined["Datetime"] = pd.to_datetime(combined["Datetime"], errors="coerce")
    combined = combined.dropna()
    fig4 = calplot(
        combined,
        x="Datetime",
        y="Canx",
        dark_theme=True,
        colorscale="reds",
        total_height=300,
    )

    try:
        current_aircraft = api.getAircraftData(selected_aircraft)
        max_crosswind = current_aircraft["crosswind"]
        altitude = current_aircraft["altitude"]
        ceiling = current_aircraft["ceiling"]
        rcr = current_aircraft["RCR"]
        takeoff_time = current_aircraft["takeoffTime"]
        landing_time = current_aircraft["landingTime"]

        max_crosswind = "Crosswind: " + str(max_crosswind)
        altitude = "Altitude: " + str(altitude)
        ceiling = "Celing: " + str(ceiling)
        rcr = "Runway Condition: " + str(rcr)
        takeoff_time = "Takeoff Time: " + str(takeoff_time)
        landing_time = "Landing Time: " + str(landing_time)

    except:
        max_crosswind = "Max Crosswind: "
        altitude = "Altitude: "
        ceiling = "Celing: "
        rcr = "Runway Condition: "
        takeoff_time = "Takeoff Time: "
        landing_time = "Landing Time: "

    return (
        fig,
        fig2,
        fig3,
        fig4,
        months[month],
        max_crosswind,
        altitude,
        ceiling,
        rcr,
        takeoff_time,
        landing_time,
    )
