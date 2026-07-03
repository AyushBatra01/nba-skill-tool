import pandas as pd

from src.db.save import save_table
from src.db.load import load_table
from src.nba_api_wrapper.playerinfo import player_info
from tqdm import tqdm

dfs = []

all_players = load_table("basic_info")['PLAYER_ID'].unique()

for player_id in tqdm(all_players):
    info = player_info(player_id, sleep=3)
    dfs.append(info)

final_df = pd.concat(dfs)

save_table(final_df, "players")

