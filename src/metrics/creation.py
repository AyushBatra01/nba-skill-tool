import pandas as pd
import numpy as np

from src.api.basic import traditional, possessions
from src.api.tracking import tracking_raw
from src.api.playtype import playtype_raw

def get_creation_metrics(season, minimum=100):
    # Retrieve Data
    base = traditional(season, columns=['MIN', 'PTS', 'FGA', 'FTA', 'AST', 'TOV'])
    poss_df = possessions(season)
    drives = tracking_raw(
        season,
        pt_measure_type='Drives',
        columns=['DRIVES', 'DRIVE_PTS', 'DRIVE_AST', 'DRIVE_TOV']
    )
    postup = tracking_raw(
        season,
        pt_measure_type='PostTouch',
        columns=['POST_TOUCHES', 'POST_TOUCH_PTS', 'POST_TOUCH_AST', 'POST_TOUCH_TOV']
    )
    touches = tracking_raw(
        season,
        pt_measure_type='Possessions',
        columns=['TOUCHES', 'TIME_OF_POSS']
    )
    passing = tracking_raw(
        season,
        pt_measure_type='Passing',
        columns=['PASSES_MADE', 'FT_AST', 'SECONDARY_AST', 'POTENTIAL_AST', 'AST_PTS_CREATED']
    )
    iso = playtype_raw(season, playtype='Isolation', columns=['POSS', 'PTS'])
    pr_ball = playtype_raw(season, playtype='PRBallHandler', columns=['POSS', 'PTS'])
    handoff = playtype_raw(season, playtype='Handoff', columns=['POSS', 'PTS'])

    # Rename
    iso = iso.rename(columns={'POSS': 'ISO_POSS', 'PTS': 'ISO_PTS'})
    pr_ball = pr_ball.rename(columns={'POSS': 'PNRBH_POSS', 'PTS': 'PNRBH_PTS'})
    handoff = handoff.rename(columns={'POSS': 'HANDOFF_POSS', 'PTS': 'HANDOFF_PTS'})

    # Filter
    base = base[base['MIN'] >= minimum]

    # Merge
    base = base.merge(poss_df, on='PLAYER_ID', how='inner')
    base = base.merge(drives, on='PLAYER_ID', how='left').fillna(0)
    base = base.merge(postup, on='PLAYER_ID', how='left').fillna(0)
    base = base.merge(touches, on='PLAYER_ID', how='left').fillna(0)
    base = base.merge(passing, on='PLAYER_ID', how='left').fillna(0)
    base = base.merge(iso, on='PLAYER_ID', how='left').fillna(0)
    base = base.merge(pr_ball, on='PLAYER_ID', how='left').fillna(0)
    base = base.merge(handoff, on='PLAYER_ID', how='left').fillna(0)

    eps = 1e-8

    # Box Score Stats
    base['Shots'] = base['FGA'] + 0.44 * base['FTA']
    base['TSP'] = base['PTS'] / (2 * base['Shots'] + eps)
    base['TOVP'] = base['TOV'] / (base['Shots'] + base['TOV'] + eps)
    base['Score'] = base['PTS'] * base['TSP']
    base['Pass'] = base['AST'] * base['AST'] / (base['AST'] + base['TOV'] + eps)
    base['Double'] = base['Score'] * base['Pass']
    base['Add'] = ((base['PTS'] + base['AST']) ** 2) / (base['Shots'] + base['AST'] + base['TOV'] + eps)

    # Decision-Making + Advanced Passing
    base['POTENTIAL_AST'] = np.where(base['AST'] > base['POTENTIAL_AST'], base['AST'], base['POTENTIAL_AST'])
    base['PA_100'] = 100 * base['POTENTIAL_AST'] / base['POSS']
    base['AST_RATE'] = (base['POTENTIAL_AST'] + base['SECONDARY_AST'] + base['FT_AST']) / (base['PASSES_MADE'] + eps)
    base['PTS_PER_AST'] = base['AST_PTS_CREATED'] / (base['AST'] + eps)
    base['TOUCH_100'] = 100 * base['TOUCHES'] / base['POSS']
    base['SCORE_RATE'] = base['PTS'] / (base['TOUCHES'] + eps)
    base['SEC_PER_TOUCH'] = 60 * base['TIME_OF_POSS'] / (base['TOUCHES'] + eps)
    base['QuickDecision'] = 100 * (base['AST_RATE'] * base['PTS_PER_AST'] + base['SCORE_RATE']) / (base['SEC_PER_TOUCH'] + eps)

    # Rim Pressure
    base['DRIVE_RATE'] = base['DRIVES'] / (base['TOUCHES'] + eps)
    base['POST_RATE'] = base['POST_TOUCHES'] / (base['TOUCHES'] + eps)
    base['RIM'] = base['DRIVES'] + base['POST_TOUCHES'] + eps
    base['RIM_PTS'] = base['DRIVE_PTS'] + base['POST_TOUCH_PTS']
    base['RIM_AST'] = base['DRIVE_AST'] + base['POST_TOUCH_AST']
    base['RIM_TOV'] = base['DRIVE_TOV'] + base['POST_TOUCH_TOV']
    base['RIM_100'] = 100 * base['RIM'] / base['POSS']
    base['RIM_RATE'] = base['RIM'] / (base['TOUCHES'] + eps)
    base['RIM_SCORE_RATE'] = (base['RIM_PTS'] + base['PTS_PER_AST'] * base['RIM_AST']) / (base['RIM'] + eps)
    base['RIM_TOV_RATE'] = base['RIM_TOV'] / (base['RIM'] + eps)
    base['RimPressure'] = base['RIM_RATE'] * (base['RIM_SCORE_RATE'] * (1 - base['RIM_TOV_RATE']))

    # Isolation
    base['ISO_PTS_100'] = 100 * base['ISO_PTS'] / base['POSS']
    base['ISO_PPP'] = base['ISO_PTS'] / (base['ISO_POSS'] + eps)
    base['Iso'] = base['ISO_PTS_100'] * base['ISO_PPP']

    # PnR
    base['PNR_PTS_100'] = 100 * (base['PNRBH_PTS'] + base['HANDOFF_PTS']) / base['POSS']
    base['PNR_PPP'] = (base['PNRBH_PTS'] + base['HANDOFF_PTS']) / (base['PNRBH_POSS'] + base['HANDOFF_POSS'] + eps)
    base['PnR'] = base['PNR_PTS_100'] * base['PNR_PPP']

    # Style
    base['ShotPARatio'] = base['Shots'] / (base['PA_100'] + eps)

    return base