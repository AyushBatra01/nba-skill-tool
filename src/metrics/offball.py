import pandas as pd
import numpy as np

from src.nba_api_wrapper.basic import traditional, possessions
from src.nba_api_wrapper.tracking import tracking_raw
from src.nba_api_wrapper.playtype import playtype_raw
from src.nba_api_wrapper.hustle import hustle

def get_offball_metrics(season, minimum=100):
    # Retrieve Data
    base = traditional(season, columns=['MIN', 'FG3A', 'FG3M', 'FTM', 'FTA'])
    poss_df = possessions(season)
    offscreen = playtype_raw(season, playtype='OffScreen', columns=['POSS', 'PTS'])
    spotup = playtype_raw(season, playtype='Spotup', columns=['POSS', 'PTS'])
    cut = playtype_raw(season, playtype='Cut', columns=['POSS', 'PTS'])
    roll = playtype_raw(season, playtype='PRRollman', columns=['POSS', 'PTS'])
    screen = hustle(season, columns=['SCREEN_ASSISTS'])
    cs = tracking_raw(
        season,
        pt_measure_type='CatchShoot',
        columns=['CATCH_SHOOT_PTS', 'CATCH_SHOOT_FGA']
    )
    
    # Rename
    offscreen = offscreen.rename(columns={'POSS': 'OFFSCREEN_POSS', 'PTS': 'OFFSCREEN_PTS'})
    spotup = spotup.rename(columns={'POSS': 'SPOTUP_POSS', 'PTS': 'SPOTUP_PTS'})
    cut = cut.rename(columns={'POSS': 'CUT_POSS', 'PTS': 'CUT_PTS'})
    roll = roll.rename(columns={'POSS': 'ROLLMAN_POSS', 'PTS': 'ROLLMAN_PTS'})
    screen = screen.rename(columns={'SCREEN_ASSISTS' : 'ScreenAst'})

    # Filter
    base = base[base['MIN'] >= minimum]

    # Merge
    base = base.merge(poss_df, on='PLAYER_ID', how='inner')
    base = base.merge(offscreen, on='PLAYER_ID', how='left').fillna(0)
    base = base.merge(spotup, on='PLAYER_ID', how='left').fillna(0)
    base = base.merge(cut, on='PLAYER_ID', how='left').fillna(0)
    base = base.merge(roll, on='PLAYER_ID', how='left').fillna(0)
    base = base.merge(screen, on='PLAYER_ID', how='left').fillna(0)
    base = base.merge(cs, on='PLAYER_ID', how='left').fillna(0)

    eps = 1e-8

    # Normalize per 100
    normalize_cols = [
        'FG3A', 'FG3M', 'OFFSCREEN_PTS', 'OFFSCREEN_POSS', 'SPOTUP_PTS', 'SPOTUP_POSS',
        'CUT_PTS', 'CUT_POSS', 'ROLLMAN_PTS', 'ROLLMAN_POSS', 'ScreenAst',
        'CATCH_SHOOT_PTS', 'CATCH_SHOOT_FGA'
    ]
    for stat in normalize_cols:
        base[stat] = 100 * base[stat] / base['POSS']

    # Box Score
    base['3P%'] = base['FG3M'] / (base['FG3A'] + eps)
    base['mult'] = 2 * (np.exp(base['FG3A']) / (1 + np.exp(base['FG3A'])) - 0.5)
    base['TPP'] = base['3P%'] * base['mult']
    base['TPS'] = (base['3P%'] ** 2) * base['FG3A']
    base['FT%'] = base['FTM'] / (base['FTA'] + eps)
    baseline_ftp = 0.75
    baseline_fta = 30
    base['FTP'] = (base['FTM'] + baseline_ftp * baseline_fta) / (base['FTA'] + baseline_fta)

    # Off Screen
    base['OFFSCREEN_PPP'] = base['OFFSCREEN_PTS'] / (base['OFFSCREEN_POSS'] + eps)
    base['OffScreen'] = base['OFFSCREEN_PTS'] * base['OFFSCREEN_PPP']

    # Spot Up
    base['SPOTUP_PPP'] = base['SPOTUP_PTS'] / (base['SPOTUP_POSS'] + eps)
    base['SpotUp'] = base['SPOTUP_PTS'] * base['SPOTUP_PPP']

    # Cuts
    base['CUT_PPP'] = base['CUT_PTS'] / (base['CUT_POSS'] + eps)
    base['Cut'] = base['CUT_PTS'] * base['CUT_PPP']

    # P&R Rollman
    base['ROLLMAN_PPP'] = base['ROLLMAN_PTS'] / (base['ROLLMAN_POSS'] + eps)
    base['Rollman'] = base['ROLLMAN_PTS'] * base['ROLLMAN_PPP']

    # Screen Assists
    base['3P_CUT_RATE'] = base['FG3A'] / (
                base['FG3A'] + base['CUT_POSS'] + base['ScreenAst'] + base['ROLLMAN_POSS'] + eps)

    # C&S
    base['CS_PPP'] = base['CATCH_SHOOT_PTS'] / (base['CATCH_SHOOT_FGA'] + eps)
    base['CatchShoot'] = base['CATCH_SHOOT_PTS'] * base['CS_PPP']

    return base
