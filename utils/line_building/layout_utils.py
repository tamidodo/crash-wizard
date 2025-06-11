import dash_mantine_components as dmc
import numpy as np
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import feffery_antd_components as fac
from coolname import generate_slug
from dash_iconify import DashIconify


def line_building_filters(df):
    tourney_list = df["Tournament"].unique()
    tourney_game_data = []
    for tourney in tourney_list:
        game_list = df[df["Tournament"] == tourney]["Game"].unique()
        tourney_game_data.append(
            [{"key": game, "value": game, "title": game} for game in game_list]
        )
    tree_data = [
        {
            "key": "All",
            "value": "all",
            "title": "All",
            "children": [
                {
                    "key": tourney_list[i],
                    "value": tourney_list[i],
                    "title": tourney_list[i],
                    "children": tourney_game_data[i],
                }
                for i in range(len(tourney_list))
            ],
        }
    ]
    return [
        html.Div("Controls and Filters", className="tab-title"),
        dmc.Space(h=20),
        dmc.Divider(
            label="Full Page Controls",
            labelPosition="center",
            color="rgb(31,67,128)",
        ),
        dmc.Space(h=10),
        dmc.CheckboxGroup(
            id="lb-handlers-cutters",
            label="Filter by Position",
            orientation="horizontal",
            offset="xs",
            children=[
                dmc.Checkbox(
                    label="Handlers",
                    value="handler",
                    color="blue",
                ),
                dmc.Checkbox(
                    label="Cutters",
                    value="cutter",
                    color="blue",
                ),
            ],
            value=["handler", "cutter"],
        ),
        dmc.Space(h=15),
        dmc.Text("Filter by Game/Tournament", size="sm", weight=500),
        dmc.Space(h=10),
        fac.AntdTreeSelect(
            id="lb-tourney-game-select",
            treeData=tree_data,
            treeCheckable=True,
            multiple=True,
            treeDefaultExpandAll=True,
            value="all",
        ),
        dmc.Space(h=10),
        dmc.Text("Choose Efficiency Type", size="sm", weight=500),
        dmc.Space(h=10),
        dmc.SegmentedControl(
            id="lb-eff-type",
            data=["Offence", "Defence", "Total"],
            value="Total",
            style={"height": "fit-content"},
        ),
        dmc.Space(h=20),
        dmc.Divider(
            label="Partner Efficiency Correlation Controls",
            labelPosition="center",
            color="rgb(31,67,128)",
        ),
        dmc.Space(h=10),
        html.Div(
            dmc.Button(
                id="lb-xy-match-select",
                children="Match X Axis to Y Axis",
                variant="filled",
                style={"margin-left": "auto"},
            ),
            style={"display": "flex"},
        ),
        dmc.MultiSelect(
            id="lb-y-player-select", label="Select Y Axis Players", searchable=True
        ),
        dmc.Space(h=10),
        dmc.MultiSelect(
            id="lb-x-player-select", label="Select X Axis Players", searchable=True
        ),
        dmc.Space(h=20),
        dmc.Divider(
            label="Pod Efficiency Correlation Controls",
            labelPosition="center",
            color="rgb(31,67,128)",
        ),
        dmc.Space(h=10),
        html.Div(
            children=[
                dmc.Text("Full Player List", size="sm", weight=500),
                dmc.Text(
                    "Potential Pod",
                    size="sm",
                    weight=500,
                    style={"margin-left": "auto"},
                ),
            ],
            style={"display": "flex", "flex-direction": "row"},
        ),
        dmc.Space(h=10),
        dmc.TransferList(id="lb-pod-maker", value=[[], []]),
        dmc.Space(h=10),
        html.Div(
            dmc.Button(
                id="lb-create-pod",
                children="Create Pod",
                variant="variant",
                style={"margin-left": "auto"},
            ),
            style={"display": "flex", "flex-direction": "row"},
        ),
        dmc.Text("Active Pods", size="sm", weight=500),
        html.Div(id="lb-pods", children=[]),
    ]


def pod_group(players):
    """Creates a single pod layout"""
    pod_name = generate_slug(2).replace("-", " ").title()
    players = ", ".join([item["value"] for item in players])
    return html.Div(
        id={"type": "pod-row", "index": pod_name},
        children=[
            dmc.Badge(
                pod_name,
                variant="gradient",
                gradient={"from": "rgb(1,113,152)", "to": "rgb(140,212,234)"},
                size="lg",
                id={"type": "pod-name", "index": pod_name},
            ),
            html.Div(
                players,
                className="pod-title",
                id={"type": "pod-players", "index": pod_name},
            ),
            dmc.ActionIcon(
                id={"type": "delete-pod", "index": pod_name},
                children=DashIconify(icon="octicon:trash-24"),
                color="red",
                variant="outline",
                style={"margin-left": "auto"},
            ),
        ],
        className="flex-row",
    )


def make_heatmap(df, custom_data, x_players, y_players, eff_type):
    fig = px.imshow(
        df,
        labels=dict(color=f"{eff_type} Efficiency"),
        x=x_players,
        y=y_players,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="ylgnbu",
    )
    fig.update(
        data=[
            {
                "customdata": np.array(custom_data),
                "hovertemplate": "Players: %{x} and %{y}<br> Number of Points Played Together: %{customdata}<br>Efficiency: %{z}",
            }
        ]
    )
    fig.update_traces(name="")
    fig.update_xaxes(side="top")
    return fig


def make_pod_bars(df):
    fig = px.bar(
        df,
        x="Pod",
        y="Efficiency",
        text_auto=True,
        hover_data="Number of Points Played Together",
    )
    fig.update_traces(marker_color="rgb(1,113,152)")
    return fig
