import numpy as np
import pandas as pd

from src.api.basic import per100, possessions, get_height
from src.api.defense import get_matchups

def assign_positions(df, min_poss):
    # Filter
    df = df.copy()
    df = df[df['POSS'] >= min_poss]

    # Sort players by height then role score
    df['ROLE_SCORE'] = df['AST'] - 0.5 * df['REB']
    df = df.sort_values(by=['HEIGHT', 'ROLE_SCORE'], ascending=[True, True]).reset_index(drop=True)

    # partition sorted list into positions
    total_poss = df['POSS'].sum()
    df['cum_poss'] = df['POSS'].cumsum()
    df['cum_frac'] = df['cum_poss'] / total_poss
    conditions = [
        df['cum_frac'] <= 0.20,
        df['cum_frac'] <= 0.40,
        df['cum_frac'] <= 0.60,
        df['cum_frac'] <= 0.80,
    ]
    positions = ['PG', 'SG', 'SF', 'PF']
    df['POSITION'] = np.select(
        conditions,
        positions,
        default='C'
    )
    return df[['OFF_PLAYER_ID', 'OFF_PTS', 'HEIGHT', 'POSS', 'POSITION']]


def matchup_difficulty(season, min_poss=200):
    # stats for offensive players
    offense = per100(season, ['PTS', 'AST', 'REB'])
    poss_df = possessions(season)
    ht = get_height(season)

    # get matchups
    matchups = get_matchups(season)

    # gather offensive stats
    off_players = ht.merge(offense, on='PLAYER_ID')
    off_players = off_players.merge(poss_df, on='PLAYER_ID')
    off_players = off_players.rename(columns={'PLAYER_ID': 'OFF_PLAYER_ID', 'PTS': 'OFF_PTS'})

    # divide offensive players into positions
    off_players = assign_positions(off_players, min_poss)

    # join offensive players
    matchups = matchups.merge(off_players, on='OFF_PLAYER_ID', how='inner')

    # Versatility
    grouped = matchups.groupby(['DEF_PLAYER_ID', 'POSITION'])['PARTIAL_POSS'].sum().reset_index()
    grouped['TOTAL_POSS'] = grouped.groupby('DEF_PLAYER_ID')['PARTIAL_POSS'].transform('sum')
    grouped['FRACTION'] = grouped['PARTIAL_POSS'] / grouped['TOTAL_POSS']
    versatility = (
        grouped.groupby('DEF_PLAYER_ID')['FRACTION']
        .apply(lambda x: -(x * np.log(x + 1e-8)).sum() / np.log(5))
        .reset_index(name='Matchup_Vers')
    )

    # Matchup Difficulty
    matchups['weighted_PTS'] = matchups['PARTIAL_POSS'] * matchups['OFF_PTS']
    by_defender = matchups.groupby('DEF_PLAYER_ID')[['weighted_PTS', 'PARTIAL_POSS']].sum()
    by_defender['Matchup_Diff'] = by_defender['weighted_PTS'] / by_defender['PARTIAL_POSS']
    by_defender = by_defender.reset_index()
    by_defender = by_defender.merge(versatility, on='DEF_PLAYER_ID', how='inner')
    by_defender = by_defender.rename(columns={'DEF_PLAYER_ID': 'PLAYER_ID'})

    return by_defender[['PLAYER_ID', 'Matchup_Diff', 'Matchup_Vers']]