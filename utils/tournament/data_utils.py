import pandas as pd
import numpy as np


def calculate_max_score_runs(df, game):
    """Calculates the highest number of points our team and our opponents scored in a row"""
    df_score_counter = df[df["player"] == df["player"].values[0]]
    num_score_us = 0
    num_score_them = 0
    if len(game) > 1:  # if more than one game, check runs for each game separately
        df_score_counter_list = []
        for game_name in df_score_counter["game"].unique():
            df_score_counter_list.append(
                df_score_counter[df_score_counter["game"] == game_name]
            )
    else:
        df_score_counter_list = [df_score_counter]
    for df_sc in df_score_counter_list:
        for k, v in df_sc.groupby(
            (df_sc["crash_scored"].shift() != df_sc["crash_scored"]).cumsum()
        ):
            if v["crash_scored"].values[0] == True and len(v) > num_score_us:
                num_score_us = len(v)
            elif v["crash_scored"].values[0] == False and len(v) > num_score_them:
                num_score_them = len(v)
    return num_score_us, num_score_them


def most_player_ds(df):
    """Calculates which player(s) had the most direct Ds"""
    max_ds = df["Player_Forced_Ds"].max()
    who_ds = df[df["Player_Forced_Ds"] == max_ds]["player"].unique()
    if len(who_ds) > 1:
        who_ds = ", ".join(who_ds)
    else:
        who_ds = who_ds[0]
    return max_ds, who_ds


def most_assists_scores(df, only_one=None):
    """Calculates which player(s) had the most scores + assists (or just one if specified) and how many that was"""
    df_sa = df[
        (df["Player_Scored/Assisted"] == "Score")
        | (df["Player_Scored/Assisted"] == "Assist")
    ]
    most_sa = 0
    most_sa_player = ["Not Recorded"]
    for player in df_sa["player"].unique():
        sa_num = len(df_sa[df_sa["player"] == player])
        if sa_num == most_sa:
            most_sa_player.append(player)
        if sa_num > most_sa:
            most_sa_player = [player]
            most_sa = sa_num
    if len(most_sa_player) > 1:
        most_sa_player = ", ".join(most_sa_player)
    else:
        most_sa_player = most_sa_player[0]
    if most_sa_player == "Not Recorded":
        most_sa = ""
    return most_sa, most_sa_player


def calculate_player_efficiency(df, o_d, best=False, line=True):
    """Calculates player efficiency on either O or D"""
    if o_d != "Total":
        df_filtered = df[(df["offence_defence"] == o_d) & (df["played"] == True)]
    else:
        df_filtered = df[df["played"] == True]
    player_list = df_filtered["player"].unique()
    df_efficiency = []
    if best:
        best_eff = 0
        best_eff_player = ["We did real bad"]
    for player in player_list:
        df_player = df_filtered[(df_filtered["player"] == player)]
        if line:
            df_player_scored = df_player[df_player["crash_scored"] == True]
        else:
            df_player_scored = df_player[
                (df_player["Player_Scored/Assisted"] == "Score")
                | (df_player["Player_Scored/Assisted"] == "Assist")
            ]
        player_efficiency = round(len(df_player_scored) / len(df_player), 2)
        if best:
            if player_efficiency == best_eff:
                best_eff_player.append(player)
            if player_efficiency > best_eff:
                best_eff_player = [player]
                best_eff = player_efficiency
        df_efficiency.append(
            {
                "player": player,
                "Efficiency": player_efficiency * 100,
            }
        )
    df_efficiency = pd.DataFrame(df_efficiency)
    if best:
        return best_eff, ", ".join(best_eff_player)
    else:
        return df_efficiency


def calculate_player_points_played(df, stack_type, line=True):
    """Creates a dataframe of how many points each player played"""
    if stack_type == "Offence/Defence":
        df = df[["player", "offence_defence", "played"]]
        df = df.groupby(["player", "offence_defence"]).sum().reset_index()
        df_points = df.pivot_table(
            values="played", index="player", columns="offence_defence"
        ).reset_index().fillna(0)
        df_points["Total"] = df_points["O"] + df_points["D"]
    if stack_type == "Line Scores/Doesn't Score":
        if line:
            df = df[["player", "crash_scored", "played"]]
            df.loc[df["crash_scored"] == True, "crash_scored"] = "Crash Score"
            df.loc[df["crash_scored"] == False, "crash_scored"] = "They Score"
            df = df.groupby(["player", "crash_scored"]).sum().reset_index()
            df_points = df.pivot_table(
                values="played", index="player", columns="crash_scored"
            ).reset_index().fillna(0)
            df_points["Total"] = df_points["Crash Score"] + df_points["They Score"]
        else:
            df = df[["player", "Player_Scored/Assisted", "played"]]
            df = df.groupby(["player", "Player_Scored/Assisted"]).count().reset_index()
            df_points = df.pivot_table(
                values="played", index="player", columns="Player_Scored/Assisted"
            ).reset_index().fillna(0)

    if stack_type == "% of Total":
        df["Played_Group"] = df["played"]
        print(df)
        df.loc[df["Played_Group"] == True, "Played_Group"] = "Played"
        df.loc[df["Played_Group"] == False, "Played_Group"] = "Sideline"
        df = df[["player", "Played_Group", "played"]]
        df = df.groupby(["player", "Played_Group"]).count().reset_index()
        df_points = df.pivot_table(
            values="played", index="player", columns="Played_Group"
        ).reset_index().fillna(0)

    return df_points


def make_scoring_story_df(df):
    """Formats the data into a way that we can show it as a scoring story line graph"""
    df = df[df["player"] == df["player"].values[0]]
    df_filtered = df[["point", "half", "crash_scored", "crash_turns"]]
    df_filtered["opponent_scored"] = ~df_filtered["crash_scored"]
    df_filtered["crash_scored"] = df_filtered["crash_scored"].cumsum()
    df_filtered["opponent_scored"] = df_filtered["opponent_scored"].cumsum()
    return df_filtered
