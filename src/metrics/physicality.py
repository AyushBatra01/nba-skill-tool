import pandas as pd
import numpy as np

from src.nba_api_wrapper.basic import traditional, possessions, get_misc, get_height
from src.nba_api_wrapper.tracking import tracking_raw
from src.nba_api_wrapper.hustle import hustle
from sklearn.linear_model import LinearRegression

def residual(df, x, y):
    model = LinearRegression().fit(X=df[[x]], y=df[y])
    yhat = model.predict(df[[x]])
    yhat = np.clip(yhat, 0, None)
    resid = df[y] - yhat
    return resid

def get_physicality_metrics(season, minimum=100):
    # Retrieve Data
    base = traditional(season, columns=['MIN', 'BLK'])
    poss_df = possessions(season)
    misc = get_misc(season)
    ht = get_height(season)
    reb = tracking_raw(
        season,
        pt_measure_type='Rebounding',
        columns=['OREB', 'OREB_CONTEST', 'DREB', 'DREB_CONTEST']
    )
    hust = hustle(season, columns=['LOOSE_BALLS_RECOVERED', 'CHARGES_DRAWN', 'BOX_OUTS'])

    # Filter
    base = base[base['MIN'] >= minimum]

    # Merge
    base = base.merge(poss_df, on='PLAYER_ID', how='inner')
    base = base.merge(ht, on='PLAYER_ID', how='inner')
    base = base.merge(misc, on='PLAYER_ID', how='left').fillna(0)
    base = base.merge(reb, on='PLAYER_ID', how='left').fillna(0)
    base = base.merge(hust, on='PLAYER_ID', how='left').fillna(0)

    # Normalize per 100
    normalize_cols = [
        'PTS_FB', 'PTS_PAINT', 'PFD', 'BLK', 'OREB_CONTEST', 'DREB_CONTEST',
        'LOOSE_BALLS_RECOVERED', 'CHARGES_DRAWN', 'BOX_OUTS'
    ]
    for stat in normalize_cols:
        base[stat] = 100 * base[stat] / base['POSS']

    # Adjusted BLk/REB vs height
    base['AdjOREB'] = residual(base, x='HEIGHT', y='OREB_CONTEST')
    base['AdjDREB'] = residual(base, x='HEIGHT', y='DREB_CONTEST')
    base['AdjBLK'] = residual(base, x='HEIGHT', y='BLK')

    # Hustle
    base['Hustle'] = base['LOOSE_BALLS_RECOVERED'] + base['CHARGES_DRAWN'] + base['BOX_OUTS']/2
    base = base.rename(columns={'HEIGHT' : 'PHYS_HEIGHT'})

    return base

