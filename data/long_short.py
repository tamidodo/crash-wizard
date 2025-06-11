import pandas as pd


df = pd.read_csv("crash_app_db_raw.csv", header=0)
# Sample columns to identify players on each point
player_columns = ["player_1", "player_2", "player_3", "player_4", "player_5", "player_6", "player_7"]

# Create long-form list of rows
long_rows = []

# Step 1: Get players per tournament
tournament_players = (
    df[player_columns + ["tournament"]]
    .melt(id_vars="tournament", value_name="player")
    .dropna()
    .groupby("tournament")["player"]
    .unique()
    .to_dict()
)

# Step 2: Iterate through each row (point)
for _, row in df.iterrows():
    tournament = row["tournament"]
    players_at_tournament = tournament_players.get(tournament, [])
    played_this_point = set(row[player_columns].dropna())
    forced_ds = row["player_forced_ds"] or []

    if not isinstance(forced_ds, list):
        forced_ds = [forced_ds]

    for player in players_at_tournament:
        long_rows.append({
            "tournament": tournament,
            "game": row["game"],
            "point": row["point"],
            "half": row["half"],
            "offence_defence": row["offence_defence"],
            "player": player,
            "played": player in played_this_point,
            "Player_Scored/Assisted": (
                "Score" if player == row["player_scored"]
                else "Assist" if player == row["player_assisted"]
                else None
            ),
            "Player_Forced_Ds": forced_ds.count(player),
            "crash_scored": row["crash_scored"],
            "crash_turns": row["crash_turns"]
        })

# Step 3: Create long-form DataFrame
long_df = pd.DataFrame(long_rows)
long_df.to_csv("crash_app_db.csv", index=False)