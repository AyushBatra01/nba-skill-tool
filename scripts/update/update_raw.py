import pandas as pd

from src.utils.general import SEASON_START, SEASON_END
from src.db.save import save_table
from src.nba_api_wrapper.basic import basic_info

all_dfs = []

for season in range(SEASON_START, SEASON_END+1):
    print(f"Processing {season}")
    df = basic_info(season, minimum=100)
    all_dfs.append(df)

final_df = pd.concat(all_dfs)

save_table(final_df, "basic_info")