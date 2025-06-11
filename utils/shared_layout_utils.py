from dash import html
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import pandas as pd
import plotly.express as px
from datetime import timedelta
from datetime import datetime as dt


def header(app, header_background_color="transparent"):
    logo = html.Img(src=app.get_asset_url("images/crash_logo.png"))
    crash_logo = html.A(
        logo,
        href="https://docs.google.com/spreadsheets/d/1zPc3dfNlMVhOP5MXOJyKVIq5wEkfm9Uf-Qb6PuP5UuA/edit?usp=sharing",
        target="_blank",
        className="header-logos-left",
    )

    header = html.Div(
        [
            html.Div(
                [
                    html.Div("Crash Data Wizard", style={"color": "rgb(217,48,49)"}),
                ],
                className="header-title",
            ),
        ],
    )

    return html.Div(
        [crash_logo, header],
        className="header",
        style={"background-color": header_background_color},
    )


def ss_cards(card_id, card_text, icon, icon_color):
    card_icon = {
        "color": "black",
        "textAlign": "center",
        "fontSize": 20,
        "margin": "auto",
    }
    return dmc.LoadingOverlay(
        dbc.CardGroup(
            [
                dbc.Card(
                    dbc.CardBody(
                        [
                            html.H4(
                                id=card_id,
                                className="font",
                            ),
                            html.P(
                                card_text,
                                id=card_id + "-label",
                                className="font",
                            ),
                        ]
                    ),
                    color="light",
                ),
                dbc.Card(
                    html.Div(className=icon, style=card_icon),
                    color=icon_color,
                    style={"maxWidth": 75},
                ),
            ],
            className="mt-4 shadow",
        ),
        loaderProps={"variant": "bars", "color": "rgb(217,48,49)", "size": "md"},
    )
