import dash_mantine_components as dmc
from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from utils.shared_layout_utils import ss_cards


def tourney_filters(df):
    tourney_list = df["tournament"].unique()
    return html.Div(
        [
            dmc.Select(
                id="tourney-select",
                label="Pick a Tournament",
                data=tourney_list,
                value=tourney_list[0],
                clearable=False,
            ),
            html.Div(
                id="game-select-div",
                style={"margin-left": "15px"},
            ),
            dmc.CheckboxGroup(
                id="tourney-handlers-cutters",
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
                style={"margin-left": "15px"},
            ),
            dmc.CheckboxGroup(
                id="tourney-game-halves",
                label="Filter by Game Half",
                orientation="horizontal",
                offset="xs",
                children=[
                    dmc.Checkbox(
                        label="First Half",
                        value="First",
                        color="blue",
                    ),
                    dmc.Checkbox(
                        label="Second Half",
                        value="Second",
                        color="blue",
                    ),
                ],
                value=["First", "Second"],
                style={"margin-left": "15px"},
            ),
            dmc.SegmentedControl(
                id="tourney-comparison-mode",
                data=["Single Game", "Game Comparison"],
                value="Single Game",
                style={"margin-left": "auto", "height": "fit-content"},
            ),
        ],
        className="flex-row",
    )


def generate_tourney_highlights(df):
    return [
        html.Div("Highlights", className="tab-title"),
        ss_cards(
            "tourney-effo",
            "Most Efficient O Player",
            "fa fa-medal",
            "rgb(255,217,77)",
        ),
        ss_cards(
            "tourney-effd",
            "Most Efficient D Player",
            "fa fa-medal",
            "rgb(255,217,77)",
        ),
        ss_cards(
            "tourney-scores-assists",
            "Most Scores + Assists",
            "fa fa-medal",
            "rgb(255,217,77)",
        ),
        ss_cards(
            "tourney-ds",
            "Most Direct Ds",
            "fa fa-medal",
            "rgb(255,217,77)",
        ),
        ss_cards(
            "tourney-max-score-us",
            "Most Points Scored in a Row",
            "fa fa-thumbs-up",
            "rgb(228,115,10)",
        ),
        ss_cards(
            "tourney-max-score-them",
            "Most Points Lost in a Row",
            "fa fa-thumbs-down",
            "rgb(228,115,10)",
        ),
        ss_cards(
            "tourney-least-turns",
            "Least Turns in 1 Point",
            "fa fa-thumbs-up",
            "rgb(228,115,10)",
        ),
        ss_cards(
            "tourney-most-turns",
            "Most Turns in 1 Point",
            "fa fa-thumbs-down",
            "rgb(228,115,10)",
        ),
    ]


def make_efficiency_bar_figure(df_efficiency):
    df_efficiency = df_efficiency.sort_values(by=["Efficiency"], ascending=False)
    fig = px.bar(df_efficiency, x="player", y="Efficiency", text_auto=True)
    fig.update_layout(
        yaxis_title="Efficiency (%)",
    )
    fig.update_traces(marker_color="rgb(1,113,152)")
    return fig


def make_points_played_bar_figure(df_points, stack_type):
    if stack_type == "Offence/Defence":
        df_points = df_points.sort_values(by=["Total"], ascending=False)
        fig = px.bar(
            df_points,
            x="player",
            y=["O", "D"],
            text_auto=True,
            color_discrete_sequence=[
                "rgb(1,113,152)",
                "rgb(255,217,77)",
                "rgb(140,212,234)",
                "rgb(228,115,10)",
            ],
        )
    if stack_type == "Line Scores/Doesn't Score":
        df_points = df_points.sort_values(by=["Total"], ascending=False)
        fig = px.bar(
            df_points,
            x="player",
            y=["Crash Score", "They Score"],
            text_auto=True,
            color_discrete_sequence=[
                "rgb(1,113,152)",
                "rgb(255,217,77)",
                "rgb(140,212,234)",
                "rgb(228,115,10)",
            ],
        )
    if stack_type == "% of Total":
        df_points = df_points.sort_values(by=["Played"], ascending=False)
        fig = px.bar(
            df_points,
            x="player",
            y=["Played", "Sideline"],
            text_auto=True,
            color_discrete_sequence=[
                "rgb(1,113,152)",
                "rgb(255,217,77)",
                "rgb(140,212,234)",
                "rgb(228,115,10)",
            ],
        )
    fig.update_layout(yaxis_title="Points Played", legend_title="")
    return fig


def make_scoring_story_fig(df_scoring, game):
    """Makes line graph that shows scoring timing"""
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_scoring["point"],
            y=df_scoring["crash_scored"],
            name="Crash Score",
            mode="lines+markers",
            line=dict(color="rgb(1,113,152)"),
            text=df_scoring["crash_turns"],
            hovertemplate="%{y}<br>Number of Crash Turns: %{text}",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_scoring["point"],
            y=df_scoring["opponent_scored"],
            name=f"{game} Score",
            mode="lines+markers",
            line=dict(color="rgb(228,115,10)"),
            text=df_scoring["crash_turns"],
            hovertemplate="%{y}<br>",
        )
    )
    # separate halves
    fig.add_vline(
        x=df_scoring.half.searchsorted("Second") + 0.5,
        line_width=2,
        line_dash="dash",
        line_color="rgb(31,67,128)",
    )
    fig.add_annotation(
        x=df_scoring.half.searchsorted("Second"),
        xanchor="right",
        y=0,
        yanchor="bottom",
        showarrow=False,
        text="First Half",
    )
    fig.add_annotation(
        x=df_scoring.half.searchsorted("Second") + 1,
        xanchor="left",
        y=0,
        yanchor="bottom",
        showarrow=False,
        text="Second Half",
    )
    fig.update_layout(
        yaxis_title="Points Scored",
        xaxis_title="Point of the Game",
        hovermode="x unified",
    )
    if len(df_scoring["crash_turns"].unique()) != 1:
        marker_size = df_scoring["crash_turns"].astype(int)
        marker_size = [x * 5 for x in marker_size]
        fig.update_traces(marker={"size": marker_size})

    return fig
