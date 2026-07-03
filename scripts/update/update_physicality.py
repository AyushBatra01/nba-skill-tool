import pandas as pd

from src.utils.general import SEASON_START, SEASON_END
from src.db.save import save_table
from src.metrics.physicality import get_physicality_metrics

all_dfs = []

for season in range(SEASON_START, SEASON_END+1):
    print(f"Processing {season}")
    df = get_physicality_metrics(season, minimum=100)
    all_dfs.append(df)

final_df = pd.concat(all_dfs)

save_table(final_df, "physicality")