import pandas as pd
import numpy as np


def make_data_for_heatmap(df, eff_type, x_players, y_players):
    """Creates dataframe of efficiencies for heat map"""
    df = df[df["played"] == True]
    if eff_type == "Offence":
        df = df[df["offence_defence"] == "O"]
    elif eff_type == "Defence":
        df = df[df["offence_defence"] == "D"]
    df_filtered = df[["player", "game", "point", "crash_scored"]]
    heatmap_data = []
    heatmap_num_data = []
    for y in y_players:
        row = []
        num_row = []
        for x in x_players:
            df_pair = df_filtered[df_filtered["player"].isin([x, y])]
            df_pair["Game_Point_ID"] = (
                df_pair["game"] + "-" + df_pair["point"].astype(str)
            )
            df_pair_tot = df_pair[df_pair["Game_Point_ID"].duplicated()][
                ["Game_Point_ID", "crash_scored"]
            ]
            if len(df_pair_tot):
                df_pair_scored = df_pair_tot[df_pair_tot["crash_scored"] == True]
                row.append(len(df_pair_scored) / len(df_pair_tot))
                if len(df_pair_tot) < 3:
                    emoji = " 💔"
                elif len(df_pair_tot) >= 3 and len(df_pair_tot) < 10:
                    emoji = " 🔥"
                elif len(df_pair_tot) >= 10:
                    emoji = " 😍"
                num_row.append(f"{len(df_pair_tot)}" + emoji)
            else:
                row.append(None)
                num_row.append(None)
        heatmap_data.append(row)
        heatmap_num_data.append(num_row)

    return heatmap_data, heatmap_num_data


def make_data_for_pod_bars(df, eff_type, pod_names, pod_players):
    """Creates dataframe of pod efficiencies for bar chart"""
    bar_data = []
    num_data = []
    for pod in range(len(pod_names)):
        df_filtered = df.loc[df["player"].isin(pod_players[pod])]
        df_filtered = df_filtered.loc[df_filtered["played"] == True]
        if eff_type == "Offence":
            df_filtered = df_filtered.loc[df_filtered["offence_defence"] == "O"]
        elif eff_type == "Defence":
            df_filtered = df_filtered.loc[df_filtered["offence_defence"] == "D"]
        df_filtered = df_filtered[["player", "game", "point", "crash_scored"]]
        df_filtered["Game_Point_ID"] = (
            df_filtered["game"] + "-" + df_filtered["point"].astype(str)
        )
        df_pod_tot = df_filtered.groupby(["Game_Point_ID"]).size().reset_index()
        df_pod_tot.columns = ["Game_Point_ID", "Count Repeats"]
        where_repeat = df_pod_tot[df_pod_tot["Count Repeats"] == len(pod_players[pod])][
            "Game_Point_ID"
        ].tolist()
        df_pod_tot = df_filtered[df_filtered["Game_Point_ID"].isin(where_repeat)][
            ["Game_Point_ID", "crash_scored"]
        ].drop_duplicates()
        if len(df_pod_tot):
            df_pod_scored = df_pod_tot[df_pod_tot["crash_scored"] == True]
            bar_data.append(len(df_pod_scored) / len(df_pod_tot))
            if len(df_pod_tot) < 3:
                emoji = " 💔"
            elif len(df_pod_tot) >= 3 and len(df_pod_tot) < 10:
                emoji = " 🔥"
            elif len(df_pod_tot) >= 10:
                emoji = " 😍"
            num_data.append(f"{len(df_pod_tot)}" + emoji)
        else:
            bar_data.append(None)
            num_data.append(None)
    df_pod_bars = pd.DataFrame(
        data={
            "Pod": pod_names,
            "Efficiency": bar_data,
            "Number of Points Played Together": num_data,
        }
    )
    return df_pod_bars
