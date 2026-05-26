import pandas as pd
import numpy as np

from src.utils.matchup_difficulty import matchup_difficulty

from src.nba_api_wrapper.basic import traditional, possessions
from src.nba_api_wrapper.defense import def_tracking
from src.nba_api_wrapper.hustle import hustle
from src.nba_api_wrapper.tracking import tracking_raw

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
    hust = hust.rename(columns={'DEFLECTIONS' : 'Deflections', 'CONTESTED_SHOTS' : 'ContestedShots'})
    dist = dist.rename(columns={'DIST_MILES_DEF' : 'DistMilesDef'})

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
        'Deflections', 'ContestedShots', 'DistMilesDef'
    ]
    for stat in normalize_cols:
        base[stat] = 100 * base[stat] / base['POSS']

    # Box Score
    base['Stock'] = base['STL'] + base['BLK']
    base['Double_def'] = base['STL'] * base['BLK']

    # Tracking
    base['AdjPMRim'] = -1 * base['PM_rim'] * np.sqrt(base['D_FGA_rim'])
    base['AdjPMAll'] = -1 * base['PM_all'] * np.sqrt(base['D_FGA_all'])

    # Tracking - perimeter only
    base['D_FGA_out'] = base['D_FGA_all'] - base['D_FGA_rim']
    base['PM_out'] = (base['D_FGA_all'] * base['PM_all'] - base['D_FGA_rim'] * base['PM_rim']) / (base['D_FGA_out'] + 1e-6)
    base['AdjPMOut'] = -1 * base['PM_out'] * np.sqrt(base['D_FGA_out'])

    # Clip Versatility
    base['ClipMatchupVers'] = np.clip(base['MatchupVers'], 0.9, 1.0)

    return base
