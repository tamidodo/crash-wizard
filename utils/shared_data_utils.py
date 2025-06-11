import pandas as pd
import numpy as np
from utils.player_mapping import PLAYER_MAP


def filter_handler_cutter(handler_cutter, df_filtered=None):
    player_list = [k for k, v in PLAYER_MAP.items() if handler_cutter in v.values()]
    if df_filtered is not None:
        df_filtered = df_filtered[df_filtered["Player"].isin(player_list)]
        return df_filtered
    else:
        return player_list
