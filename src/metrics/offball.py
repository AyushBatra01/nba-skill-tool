import pandas as pd
import numpy as np

from src.api.basic import traditional, possessions
from src.api.tracking import tracking_raw
from src.api.playtype import playtype_raw
from src.api.hustle import hustle

def get_offball_metrics(season, minimum=100):
    # Retrieve Data
    base = traditional(season, columns=['MIN', 'FG3A', 'FG3M', 'FTM', 'FTA'])
    poss_df = possessions(season)
    offscreen = playtype_raw(season, playtype='OffScreen', columns=['POSS', 'PTS'])
    spotup = playtype_raw(season, playtype='Spotup', columns=['POSS', 'PTS'])
    cut = playtype_raw(season, playtype='Cut', columns=['POSS', 'PTS'])
    roll = playtype_raw(season, playtype='PRRollman', columns=['POSS', 'PTS'])
    screen = hustle(season, columns=['SCREEN_ASSISTS'])
    dist = tracking_raw(
        season,
        pt_measure_type='SpeedDistance',
        columns=['DIST_MILES_OFF']
    )

    # Rename
    offscreen = offscreen.rename(columns={'POSS': 'OFFSCREEN_POSS', 'PTS': 'OFFSCREEN_PTS'})
    spotup = spotup.rename(columns={'POSS': 'SPOTUP_POSS', 'PTS': 'SPOTUP_PTS'})
    cut = cut.rename(columns={'POSS': 'CUT_POSS', 'PTS': 'CUT_PTS'})
    roll = roll.rename(columns={'POSS': 'ROLLMAN_POSS', 'PTS': 'ROLLMAN_PTS'})

    # Filter
    base = base[base['MIN'] >= minimum]

    # Merge
    base = base.merge(poss_df, on='PLAYER_ID', how='inner')
    base = base.merge(offscreen, on='PLAYER_ID', how='left').fillna(0)
    base = base.merge(spotup, on='PLAYER_ID', how='left').fillna(0)
    base = base.merge(cut, on='PLAYER_ID', how='left').fillna(0)
    base = base.merge(roll, on='PLAYER_ID', how='left').fillna(0)
    base = base.merge(screen, on='PLAYER_ID', how='left').fillna(0)
    base = base.merge(dist, on='PLAYER_ID', how='left').fillna(0)

    eps = 1e-8

    # Box Score
    base['FG3A_100'] = 100 * base['FG3A'] / base['POSS']
    base['3P%'] = base['FG3M'] / (base['FG3A'] + eps)
    base['mult'] = 2 * (np.exp(base['FG3A_100']) / (1 + np.exp(base['FG3A_100'])) - 0.5)
    base['TPP'] = base['3P%'] * base['mult']
    base['TPS'] = (base['3P%'] ** 2) * base['FG3A_100']
    base['FTP'] = base['FTM'] / (base['FTA'] + eps)
    base['FTP'] = np.clip(base['FTP'], 0.5, 1.0)
    base['FT%'] = base['FTP'].copy()

    # Off Screen
    base['OFFSCREEN_PTS_100'] = 100 * base['OFFSCREEN_PTS'] / base['POSS']
    base['OFFSCREEN_PPP'] = base['OFFSCREEN_PTS'] / (base['OFFSCREEN_POSS'] + eps)
    base['OffScreen'] = base['OFFSCREEN_PTS_100'] * base['OFFSCREEN_PPP']

    # Spot Up
    base['SPOTUP_PTS_100'] = 100 * base['SPOTUP_PTS'] / base['POSS']
    base['SPOTUP_PPP'] = base['SPOTUP_PTS'] / (base['SPOTUP_POSS'] + eps)
    base['SpotUp'] = base['SPOTUP_PTS_100'] * base['SPOTUP_PPP']

    # Cuts
    base['CUT_PTS_100'] = 100 * base['CUT_PTS'] / base['POSS']
    base['CUT_PPP'] = base['CUT_PTS'] / (base['CUT_POSS'] + eps)
    base['Cut'] = base['CUT_PTS_100'] * base['CUT_PPP']

    # P&R Rollman
    base['ROLLMAN_PTS_100'] = 100 * base['ROLLMAN_PTS'] / base['POSS']
    base['ROLLMAN_PPP'] = base['ROLLMAN_PTS'] / (base['ROLLMAN_POSS'] + eps)
    base['Rollman'] = base['ROLLMAN_PTS_100'] * base['ROLLMAN_PPP']

    # Screen Assists
    base['ScreenAst'] = 100 * base['SCREEN_ASSISTS'] / base['POSS']
    base['3P_CUT_RATE'] = base['FG3A'] / (
                base['FG3A'] + base['CUT_POSS'] + base['SCREEN_ASSISTS'] + base['ROLLMAN_POSS'] + eps)

    # Distance
    base['Dist'] = 100 * base['DIST_MILES_OFF'] / base['POSS']

    return base
