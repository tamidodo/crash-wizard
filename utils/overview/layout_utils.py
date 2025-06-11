import dash_ag_grid as dag
from dash import html, dcc
import pandas as pd
import numpy as np


def main_page_ag_grid(df):
    return html.Div(
        [
            html.Div(
                dcc.Markdown(
                    """
                    This dashboard (or by its more fun name, the Data Wizard) is for gaining insight into Crash's performance at tournaments
                    as a team, as well as individuals. This is based on the line calling sheets and extra stats taken when available. 

                    There are three tabs:
                    - The **Overview** tab currently contains a table with the raw data used for this app. It is grouped by Tournament > Game > Player and the 
                    columns are Point (which point in the game is it), played (True or False), crash_scored (True or False), offence_defence (Did we start on O or D), 
                    Player_Scored/Assisted (either Score, Assist or null), Player_Forced_Ds (number of Ds that player forced on that point),
                    and crash_turns (number of time we lost posession of the disc on that point). Watch this space for more highlight cards soon, as we now have more than one 
                    tournament's data!
                    - The **Line Building** tab allows you to look at the combined efficiency of players, either as pairs or as pods. 
                    Filters and Controls are split into full page controls which will filter/change mode for the whole page, and controls specific to each graph.
                    - The **Tournament Deep Dive** tab allows you to take a closer look at the overall team stats for a given tournament, either for multiple games or a single game.
                    You can see some select highlights of individual players or team stats on the left column. On the right column, if single game mode is selected,
                    you can see a graph of the team scoring throughout the game to help visualize how tight points were. For both single game and game comparison mode, there are 
                    bar graphs to show efficiency by player and number of points played per player. Some updates to keep an eye out for: now that we have data for number of turns per point,
                    I intend to add that information into the "Scoring Throughout Game" graph by sizing the markers by number of turns in that point, as well as adding a mode for the 
                    "Points Played" bar graph that shows the number of turns that occurred while a player was on. This effectively tells you similar information to number of points played but
                    better conveys the length of time a player was on for (differentiate between short points and long points).
                    The filters at the top of the page affect all visualizations on the page.

                    """,
                    style={"padding": "25px"},
                ),
                className="card",
                style={"margin": "35px"},
            ),
            html.Div(
                className="card glow",
                style={"width": "95%"},
                children=dag.AgGrid(
                    className="ag-theme-material",
                    columnSize="autoSize",
                    defaultColDef={"resizable": True, "sortable": True, "filter": "agNumberColumnFilter"},
                    dashGridOptions={"pagination": True, "paginationAutoPageSize": True},
                    rowData=df.to_dict("records"),
                    columnDefs=[
                        {"field": "tournament"},
                        {"field": "game"},
                        {"field": "player"},
                        {"field": "point"},
                        {"field": "played"},
                        {"field": "crash_scored"},
                        {"field": "offence_defence"},
                        {"field": "Player_Scored/Asssisted"},
                        {"field": "Player_Forced_Ds"},
                        {"field": "crash_turns"},
                    ],
                ),
            ),
        ]
    )
