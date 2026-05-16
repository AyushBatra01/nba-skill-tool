import pandas as pd
import numpy as np

from src.utils.matchup_difficulty import matchup_difficulty

from src.api.basic import traditional, possessions
from src.api.defense import def_tracking
from src.api.hustle import hustle
from src.api.tracking import tracking_raw

def get_defense_metrics(season, minimum=100):
    # Retrieve Data
    base = traditional(season, columns=['MIN', 'STL', 'BLK'])
    poss_df = possessions(season)
    track_all = def_tracking(season)
    track_rim = def_tracking(season, category="Less Than 6Ft")
    hust = hustle(season, columns=['DEFLECTIONS', 'CONTESTED_SHOTS'])
    md = matchup_difficulty(season, min_poss=100)
    dist = tracking_raw(season, pt_measure_type='SpeedDistance', columns=['DIST_MILES_DEF'])

    # Rename
    track_all = track_all.rename(columns={'PCT_PLUSMINUS': 'PM_all', 'D_FGA': 'D_FGA_all'})
    track_rim = track_rim.rename(columns={'PLUSMINUS': 'PM_rim', 'FGA_LT_06': 'D_FGA_rim'})

    # Filter
    base = base[base['MIN'] >= minimum]

    # Merge
    base = base.merge(poss_df, on='PLAYER_ID', how='inner')
    base = base.merge(track_all, on='PLAYER_ID', how='left').fillna(0)
    base = base.merge(track_rim, on='PLAYER_ID', how='left').fillna(0)
    base = base.merge(hust, on='PLAYER_ID', how='left').fillna(0)
    base = base.merge(md, on='PLAYER_ID', how='left').fillna(0)
    base = base.merge(dist, on='PLAYER_ID', how='left').fillna(0)

    eps = 1e-8

    # Normalize per 100
    normalize_cols = [
        'STL', 'BLK', 'D_FGA_all', 'D_FGA_rim',
        'DEFLECTIONS', 'CONTESTED_SHOTS', 'DIST_MILES_DEF'
    ]
    for stat in normalize_cols:
        base[stat] = 100 * base[stat] / base['POSS']

    # Box Score
    base['Stock'] = base['STL'] + base['BLK']
    base['Double'] = base['STL'] * base['BLK']

    # Tracking
    base['adj_PM_all'] = -1 * base['PM_all'] * np.sqrt(base['D_FGA_all'])
    base['adj_PM_rim'] = -1 * base['PM_rim'] * np.sqrt(base['D_FGA_rim'])

    # Clip Versatility
    base['Matchup_Vers'] = np.clip(base['Matchup_Vers'], 0.9, 1.0)

    return base
