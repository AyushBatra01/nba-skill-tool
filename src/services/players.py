import pandas as pd

from src.scoring.pipeline import build_skill_table, build_full_table, add_percentiles
from src.config.load_config import configs, pillar_views
from src.db.load import get_player

bio_info = ["SEASON", "TEAM", "TEAM_ID", "AGE", "MIN"]

def player_init(player_id):
    player_info = get_player(player_id)
    start = player_info['FROM_YEAR'] + 1
    end = player_info['TO_YEAR']
    return player_info, start, end

def get_player_overall(player_id, minimum=500):
    rows = []
    player_info, start, end = player_init(player_id)
    data_cols = ["Creation", "OffBall", "Defense", "Physicality", "Role", "Rating"]
    pct_cols = [f"{d}_pct" for d in data_cols]
    cols = bio_info + data_cols + pct_cols
    for season in range(start, end+1):
        # get full table
        full_df = build_full_table(season, configs, minimum)
        if player_id not in full_df['PLAYER_ID'].values:
            continue
        # compute percentiles
        full_df = add_percentiles(full_df, data_cols)
        # filter to just the player
        player_row = full_df[full_df['PLAYER_ID'] == player_id]
        player_row = player_row[cols]
        rows.append(player_row)
    if len(rows) == 0:
        return None
    final_df = pd.concat(rows)
    return final_df

def get_player_skill(player_id, skill, minimum=500):
    rows = []
    player_info, start, end = player_init(player_id)
    config = configs[skill.lower()]
    pillars = config['pillars']
    data_cols = [pillar_name for pillar_name in pillars.keys()]
    data_cols.append(skill)
    pct_cols = [f"{d}_pct" for d in data_cols]
    cols = bio_info + data_cols + pct_cols
    for season in range(start, end+1):
        # get full table
        full_df = build_skill_table(season, config, skill, minimum)
        if player_id not in full_df['PLAYER_ID'].values:
            continue
        # compute percentiles
        full_df = add_percentiles(full_df, data_cols)
        # filter to just the player
        player_row = full_df[full_df['PLAYER_ID'] == player_id]
        player_row = player_row[cols]
        rows.append(player_row)
    if len(rows) == 0:
        return None
    final_df = pd.concat(rows)
    return final_df

def get_player_pillar(player_id, skill, pillar, minimum=500):
    rows = []
    player_info, start, end = player_init(player_id)
    config = configs[skill.lower()]
    data_cols = pillar_views[skill][pillar]
    pct_cols = [f"{d}_pct" for d in data_cols]
    cols = bio_info + data_cols + pct_cols
    for season in range(start, end + 1):
        # get full table
        full_df = build_skill_table(season, config, skill, minimum)
        if player_id not in full_df['PLAYER_ID'].values:
            continue
        # compute percentiles
        full_df = add_percentiles(full_df, data_cols)
        # filter to just the player
        player_row = full_df[full_df['PLAYER_ID'] == player_id]
        player_row = player_row[cols]
        rows.append(player_row)
    if len(rows) == 0:
        return None
    final_df = pd.concat(rows)
    return final_df