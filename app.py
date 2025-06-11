from dash import (
    Dash,
    dcc,
    html,
    Input,
    Output,
    State,
    callback,
    no_update,
    ALL,
    callback_context as ctx,
)
import dash_mantine_components as dmc
import numpy as np
from datetime import datetime as dt
from datetime import timedelta
import pandas as pd
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
import os
import json

from utils.shared_layout_utils import header
from utils.shared_data_utils import filter_handler_cutter
from utils.tournament.layout_utils import (
    tourney_filters,
    generate_tourney_highlights,
    make_efficiency_bar_figure,
    make_points_played_bar_figure,
    make_scoring_story_fig,
)
from utils.tournament.data_utils import (
    calculate_max_score_runs,
    most_player_ds,
    most_assists_scores,
    calculate_player_efficiency,
    calculate_player_points_played,
    make_scoring_story_df,
)
from utils.line_building.layout_utils import (
    line_building_filters,
    pod_group,
    make_heatmap,
    make_pod_bars,
)
from utils.line_building.data_utils import make_data_for_heatmap, make_data_for_pod_bars
from utils.overview.layout_utils import main_page_ag_grid
from utils.player_mapping import PLAYER_MAP

df = pd.read_csv("data/crash_app_db.csv", header=0)

FONT_AWESOME = "https://use.fontawesome.com/releases/v6.4.0/css/all.css"

app = Dash(
    __name__,
    title="Crash Data Wizard",
    update_title=None,
    external_stylesheets=[dbc.themes.BOOTSTRAP, FONT_AWESOME],
    suppress_callback_exceptions=True,
)
server = app.server


def overview_tab():
    return [dmc.Space(h=20), main_page_ag_grid(df)]


def tourney_tab():
    return [
        html.Div("Controls and Filters", className="tab-title"),
        tourney_filters(df),
        dmc.Space(h=20),
        dmc.Divider(
            id="tourney-tab-title",
            labelPosition="center",
            size="lg",
            color="rgb(31,67,128)",
            styles={"label": {"font-size": "3vh", "line-height": 3}},
        ),
        dmc.Space(h=20),
        dmc.Grid(
            justify="center",
            gutter="md",
            style={"margin-left": "10px", "margin-right": "10px"},
            children=[
                dmc.Col(
                    span=3,
                    children=generate_tourney_highlights(df),
                ),
                dmc.Col(
                    span=9,
                    children=[
                        html.Div(id="tourney-single-content"),
                        html.Div(
                            children=[
                                html.Div(
                                    "Efficiency Comparison", className="tab-title"
                                ),
                                dmc.SegmentedControl(
                                    id="tourney-efficiency-control",
                                    data=["Offence", "Defence", "Total"],
                                    value="Total",
                                    style={
                                        "margin-left": "auto",
                                        "height": "fit-content",
                                    },
                                ),
                            ],
                            className="flex-row",
                        ),
                        html.Div(
                            className="card glow",
                            children=dcc.Graph(
                                id="tourney-eff-bars",
                            ),
                        ),
                        dmc.Space(h=20),
                        html.Div(
                            children=[
                                html.Div(
                                    "Points Played",
                                    className="tab-title",
                                ),
                                dmc.SegmentedControl(
                                    id="tourney-points-played-control",
                                    data=[
                                        "Offence/Defence",
                                        "Line Scores/Doesn't Score",
                                        "% of Total",
                                    ],
                                    value="Offence/Defence",
                                    style={
                                        "margin-left": "auto",
                                        "height": "fit-content",
                                    },
                                ),
                            ],
                            className="flex-row",
                        ),
                        html.Div(
                            className="card glow",
                            children=dcc.Graph(
                                id="tourney-points-played-bars",
                            ),
                        ),
                    ],
                ),
            ],
        ),
    ]


def line_build_tab():
    return [
        dmc.Space(h=10),
        dmc.Grid(
            justify="center",
            gutter="md",
            style={"margin-left": "10px", "margin-right": "10px"},
            children=[
                dmc.Col(
                    span=4,
                    children=line_building_filters(df),
                ),
                dmc.Col(
                    span=8,
                    children=[
                        html.Div(
                            "Partner Efficiency Correlation", className="tab-title"
                        ),
                        dmc.Space(h=15),
                        html.Div(
                            className="card glow",
                            children=dcc.Graph(
                                id="partner-eff-heatmap",
                            ),
                        ),
                        dmc.Space(h=20),
                        html.Div("Pod Efficiency Correlation", className="tab-title"),
                        dmc.Space(h=15),
                        html.Div(
                            className="card glow",
                            children=dcc.Graph(
                                id="pod-eff-bars",
                            ),
                        ),
                    ],
                ),
            ],
        ),
    ]


app.layout = dmc.MantineProvider(
    withGlobalStyles=True,
    theme={"colorScheme": "light"},
    children=dmc.NotificationsProvider(
        [
            ## Header and app description
            header(app),
            dmc.Space(h=15),
            dmc.Tabs(
                [
                    dmc.TabsList(
                        [
                            dmc.Tab("Crash At A Glance", value="1"),
                            dmc.Tab("Line Building", value="2"),
                            dmc.Tab("Tournament Deep Dive", value="3"),
                        ]
                    ),
                    dmc.TabsPanel(overview_tab(), value="1"),
                    dmc.TabsPanel(line_build_tab(), value="2"),
                    dmc.TabsPanel(tourney_tab(), value="3"),
                ],
                value="1",
            ),
        ]
    ),
)


## CALLBACKS FOR OVERVIEW TAB

## CALLBACKS FOR LINE BUILDING TAB


# Callback for main player select and pod maker
@callback(
    Output("lb-y-player-select", "data"),
    Output("lb-y-player-select", "value"),
    Output("lb-x-player-select", "data"),
    Output("lb-x-player-select", "value"),
    Output("lb-pod-maker", "value"),
    Input("lb-handlers-cutters", "value"),
    Input("lb-tourney-game-select", "value"),
    Input("lb-create-pod", "n_clicks"),
    Input("lb-xy-match-select", "n_clicks"),
    State("lb-y-player-select", "data"),
    State("lb-x-player-select", "data"),
    State("lb-y-player-select", "value"),
)
def update_player_main_select(
    handler_cutter, games, n_clicks, match_select, y_players, x_players, y_player_sel
):
    triggered_id = ctx.triggered_id
    if triggered_id == "lb-xy-match-select":
        return no_update, no_update, no_update, y_player_sel, no_update
    if "all" not in games:
        df_filtered = df[df["Game"].isin(games)]
    else:
        df_filtered = df
    if len(handler_cutter) == 1:
        df_filtered = filter_handler_cutter(handler_cutter[0], df_filtered)
    player_list = []
    filtered_players = df_filtered["Player"].unique()
    for position in handler_cutter:
        position_list = filter_handler_cutter(position)
        for player in position_list:
            if player in filtered_players:
                player_list.append(
                    {"value": player, "label": player, "group": position.capitalize()}
                )
    if triggered_id == "lb-create-pod":
        return no_update, no_update, no_update, no_update, [player_list, []]
    else:
        if player_list == x_players:
            return no_update, no_update, no_update, no_update, no_update
        return (
            player_list,
            [player_list[i]["value"] for i in range(4)],
            player_list,
            [player_list[i]["value"] for i in range(11, 15)],
            [player_list, []],
        )


# Callback to disable pod creation unless players are selected
@callback(Output("lb-create-pod", "disabled"), Input("lb-pod-maker", "value"))
def disable_pod_maker(pod_vals):
    if len(pod_vals[1]) > 1:
        return False
    else:
        return True


# Callback for pod creation
@callback(
    Output("lb-pods", "children"),
    Input("lb-create-pod", "n_clicks"),
    Input({"type": "delete-pod", "index": ALL}, "n_clicks"),
    State("lb-pods", "children"),
    State("lb-pod-maker", "value"),
    prevent_initial_call=True,
)
def update_pod_groups(create_pod, delete_pod, current_pods, pod_maker_val):
    triggered = ctx.triggered_id
    if triggered == "lb-create-pod" and create_pod > 0:
        current_pods.append(pod_group(pod_maker_val[1]))
    else:
        del_row = triggered["index"]
        current_pods = [row for row in current_pods if del_row not in str(row)]
    return current_pods


# Callback for partner heat map
@callback(
    Output("partner-eff-heatmap", "figure"),
    Input("lb-tourney-game-select", "value"),
    Input("lb-eff-type", "value"),
    Input("lb-y-player-select", "value"),
    Input("lb-x-player-select", "value"),
)
def update_partner_eff_heat_map(games, eff_type, y_players, x_players):
    if not len(y_players) or not len(x_players):
        return {"data": [], "layout": {}}
    if "all" not in games:
        df_filtered = df[df["game"].isin(games)]
    else:
        df_filtered = df
    df_filtered = df_filtered[
        (df_filtered["player"].isin(y_players))
        | (df_filtered["player"].isin(x_players))
    ]
    df_heatmap, custom_data = make_data_for_heatmap(
        df_filtered, eff_type, x_players, y_players
    )
    fig = make_heatmap(df_heatmap, custom_data, x_players, y_players, eff_type)
    return fig


# Callback for pod bars
@callback(
    Output("pod-eff-bars", "figure"),
    Input("lb-tourney-game-select", "value"),
    Input("lb-eff-type", "value"),
    Input({"type": "pod-name", "index": ALL}, "children"),
    State({"type": "pod-players", "index": ALL}, "children"),
)
def update_partner_eff_heat_map(games, eff_type, pod_names, pod_players):
    if not len(pod_names):
        return {"data": [], "layout": {}}
    if "all" not in games:
        df_filtered = df[df["game"].isin(games)]
    else:
        df_filtered = df
    pod_players = [pod.split(", ") for pod in pod_players]
    df_bars = make_data_for_pod_bars(df_filtered, eff_type, pod_names, pod_players)
    fig = make_pod_bars(df_bars)
    return fig


## CALLBACKS FOR TOURNAMENT TAB


# Callback for whether game should be single or multiselect and which games should be selectable
@callback(
    Output("game-select-div", "children"),
    Input("tourney-comparison-mode", "value"),
    Input("tourney-select", "value"),
)
def change_game_select(comp_mode, tourney):
    game_list = df[df["tournament"] == tourney]["game"].unique()
    if comp_mode == "Single Game":
        return dmc.Select(
            id="game-select",
            data=game_list,
            label="Pick a Game",
            value=game_list[0],
            clearable=False,
        )
    else:
        return dmc.MultiSelect(
            id="game-select",
            data=game_list,
            label="Pick a Game",
            value=game_list,
            clearable=False,
        )


# Callback for adjusting title of page
@callback(
    Output("tourney-tab-title", "label"),
    State("tourney-select", "value"),
    Input("game-select", "value"),
    State("tourney-comparison-mode", "value"),
    prevent_initial_call=True,
)
def change_title(tourney, game, comp_mode):
    if comp_mode == "Single Game":
        return f"{tourney}: Crash vs {game}"
    else:
        return f"{tourney}: An Overview"


# Callback for filling in values for score cards
@callback(
    Output("tourney-effo", "children"),
    Output("tourney-effd", "children"),
    Output("tourney-scores-assists", "children"),
    Output("tourney-ds", "children"),
    Output("tourney-max-score-us", "children"),
    Output("tourney-max-score-them", "children"),
    Output("tourney-least-turns", "children"),
    Output("tourney-most-turns", "children"),
    State("tourney-select", "value"),
    Input("game-select", "value"),
    Input("tourney-handlers-cutters", "value"),
    Input("tourney-game-halves", "value"),
    prevent_initial_call=True,
)
def update_score_cards(tourney, game, handler_cutter, halves):
    if type(game) != list:
        game = [game]
    df_filtered = df[(df["tournament"] == tourney) & (df["game"].isin(game))]
    if len(handler_cutter) == 1:
        df_filtered = filter_handler_cutter(handler_cutter[0], df_filtered)
    if len(halves) == 1:
        df_filtered = df_filtered[df_filtered["half"] == halves[0]]

    # To calculate the max score us and them
    num_score_us, num_score_them = calculate_max_score_runs(df_filtered, game)
    max_turns = df_filtered["crash_turns"].max()
    min_turns = df_filtered["crash_turns"].min()

    # To calculate the most ds
    max_ds, who_ds = most_player_ds(df_filtered)

    # To calculate the most assists/scores
    most_sa, most_sa_player = most_assists_scores(df_filtered)

    # To calculate efficiency on O and D
    best_eff_o, best_eff_o_player = calculate_player_efficiency(
        df_filtered, "O", best=True
    )
    best_eff_d, best_eff_d_player = calculate_player_efficiency(
        df_filtered, "D", best=True
    )

    return (
        f"{best_eff_o_player} ({best_eff_o * 100}%)",
        f"{best_eff_d_player} ({best_eff_d * 100}%)",
        f"{most_sa_player} ({most_sa})",
        f"{who_ds} ({max_ds})",
        num_score_us,
        num_score_them,
        min_turns,
        max_turns,
    )


# Callback for efficiency bar graph
@callback(
    Output("tourney-eff-bars", "figure"),
    State("tourney-select", "value"),
    Input("game-select", "value"),
    Input("tourney-handlers-cutters", "value"),
    Input("tourney-efficiency-control", "value"),
    Input("tourney-game-halves", "value"),
    prevent_initial_call=True,
)
def make_efficiency_bar_graph(
    tourney, game, handler_cutter, eff_type, halves
):
    if type(game) != list:
        game = [game]
    df_filtered = df[(df["tournament"] == tourney) & (df["game"].isin(game))]
    if len(handler_cutter) == 1:
        df_filtered = filter_handler_cutter(handler_cutter[0], df_filtered)
    if len(halves) == 1:
        df_filtered = df_filtered[df_filtered["half"] == halves[0]]
    if eff_type == "Offence":
        eff_type = "O"
    if eff_type == "Defence":
        eff_type = "D"
    df_efficiency = calculate_player_efficiency(
        df_filtered,
        eff_type,
    )
    fig = make_efficiency_bar_figure(df_efficiency)
    return fig


# Callback for points played stacked bar graph
@callback(
    Output("tourney-points-played-bars", "figure"),
    State("tourney-select", "value"),
    Input("game-select", "value"),
    Input("tourney-handlers-cutters", "value"),
    Input("tourney-points-played-control", "value"),
    Input("tourney-game-halves", "value"),
    prevent_initial_call=True,
)
def make_points_played_bar_graph(
    tourney, game, handler_cutter,stack_type, halves
):
    if type(game) != list:
        game = [game]
    df_filtered = df[(df["tournament"] == tourney) & (df["game"].isin(game))]
    if len(handler_cutter) == 1:
        df_filtered = filter_handler_cutter(handler_cutter[0], df_filtered)
    if len(halves) == 1:
        df_filtered = df_filtered[df_filtered["half"] == halves[0]]
    df_points_played = calculate_player_points_played(
        df_filtered,
        stack_type,
    )
    fig = make_points_played_bar_figure(df_points_played, stack_type)
    return fig


# Callback for extra content shown only when a single game is chosen
@callback(
    Output("tourney-single-content", "children"),
    Input("tourney-comparison-mode", "value"),
    Input("game-select", "value"),
    State("tourney-select", "value"),
    prevent_initial_call=True,
)
def add_extra_content(comp_mode, game, tourney):
    if comp_mode == "Game Comparison":
        if len(game) != 1:
            return []
    else:
        if type(game) == list:
            game = game[0]
        df_filtered = df[(df["tournament"] == tourney) & (df["game"] == game)]
        df_story = make_scoring_story_df(df_filtered)
        story_fig = make_scoring_story_fig(df_story, game)
        return [
            html.Div(
                "Scoring Throughout Game",
                className="tab-title",
                style={"margin-bottom": "20px", "margin-left": "25px"},
            ),
            html.Div(
                className="card glow",
                children=dcc.Graph(id="tourney-scoring-story-line", figure=story_fig),
            ),
        ]


if __name__ == "__main__":
    app.run_server(debug=True)
