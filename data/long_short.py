import pandas as pd


df = pd.read_csv("crash_app_db_raw.csv", header=0)
# Sample columns to identify players on each point
player_columns = ["player_1", "player_2", "player_3", "player_4", "player_5", "player_6", "player_7"]

# Create long-form list of rows
long_rows = []

for _, row in df.iterrows():
    all_players = set(row[player_columns].dropna())
    forced_ds = row["player_forced_ds"] or []
    
    # Ensure it's always a list
    if not isinstance(forced_ds, list):
        forced_ds = [forced_ds]
    
    # For every player who appeared in the game (union of all players mentioned)
    unique_players = set(all_players) | {row["player_assisted"], row["player_scored"]} | set(forced_ds)
    unique_players = {p for p in unique_players if pd.notna(p)}

    for player in unique_players:
        long_rows.append({
            "player": player,
            "tournament": row["tournament"],
            "game": row["game"],
            "point": row["point"],
            "half": row["half"],
            "played": player in all_players,
            "crash_scored": row["crash_scored"],
            "offence_defence": row["offence_defence"],
            "Player_Scored/Assisted": (
                "Score" if player == row["player_scored"]
                else "Assist" if player == row["player_assisted"]
                else None
            ),
            "crash_turns": row["crash_turns"],
            "Player_Forced_Ds": forced_ds.count(player),
        })

# Convert to DataFrame
long_df = pd.DataFrame(long_rows)
long_df.to_csv("crash_app_db.csv", index=False)